from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json, requests
from feedback_classes import *
from auth import *

json_file = "speeches_and_feedback.json"

with open(json_file, "r") as read_file:
    speech_feedback_data = json.load(read_file)

app = FastAPI()

# Accessing Quizzma Services
external_service_link = "http://tubeststrdt.a3h4epepd8gaf9ay.southeastasia.azurecontainer.io"

def get_token():
    token_url = external_service_link+"/token"
    token_response = requests.post(token_url, data={"username": "Kean", "password": "test123"})
    token = token_response.json().get("access_token")
    return token

def get_questions():
    headers= {"Authorization": f'Bearer {get_token()}'}
    questions = requests.get(external_service_link+"/questions", headers=headers)
    return questions.json()


# AUTHORIZATION PROCESS
async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                                         detail="coud not validate user credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        # parse out the token and decode it
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        # check if the user exists
        if username is None:
            raise credential_exception
        # get the user data
        token_data = TokenData(username = username)
    except JWTError:
        raise credential_exception
    
    # checks if the user exists in the database
    user = get_user(users_data, username = token_data.username)
   
    if user is None:
        raise credential_exception
    
    return user

# check if the user is enabled or disabled
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

# writing tokens
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_data, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta= access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# # get current user
# @app.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user

# Register a new user
@app.post('/register')
async def register_user(new_user: User, current_user: User = Depends(get_current_active_user)):
    user_dict = new_user.dict()
    user_found = False

    if current_user.isAdmin:
        for user in users_data:
            if new_user.username == user or new_user.user_id == user[0]:
                user_found = True
    
        if not user_found:
            createdUser = UserCreate()
            createdUser.user_id = new_user.user_id
            createdUser.username = new_user.username
            createdUser.password_preprocessed = ""
            createdUser.password_hash = get_password_hash(new_user.password_preprocessed)
            createdUser.isTutor = 0
            createdUser.isAdmin = 0
            createdUser.disabled = 0

            finalNewUser = vars(createdUser)

            users_data[new_user.username]= finalNewUser

            with open("users.json", "w") as write_file:
                json.dump(users_data, write_file, indent=2)

            return finalNewUser

        else:
            return "Username or ID taken"
    else:
        return {"message": "You are not authorized as an admin, you may not access this function"}


# @app.get("/users/me/items")
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
#     return [{"item_id": 1, "owner": current_user}]


# Home
@app.get('/')
async def read_home():
    return {"message": "Welcome to Critiquill Services"}

# returns all speeches listed in the JSON data
@app.get('/speeches')
async def read_all_speeches(current_user: User = Depends(get_current_active_user)):
    if current_user.isAdmin:
        return speech_feedback_data['speeches']
    else:
        return {"message": "You are not authorized as a tutor, you may not access this file"}

# Gets all speeches made by a certain student
@app.get('/speeches/students/{student_id}')
async def read_speech_student_id(student_id: int, current_user: User = Depends(get_current_active_user)):
    print(student_id)
    if current_user.isTutor or current_user.user_id == student_id:
        found_speech = False
        speech_arr = []
        for speech in speech_feedback_data["speeches"]:
            if speech["student_id"] == student_id:
                found_speech = True
                speech_arr.append(speech)

        if found_speech:
            return speech_arr

        raise HTTPException(
            status_code=404, detail=f'Speech with the corresponding Student ID not found'
        )
    else:
        return {"message": "you are not authorized as a tutor or you are trying to access a speech that does not belong to you. Access denied"}

# Chooses a specific speech ID
@app.get('/speeches/{speech_id}')
async def read_speech_id(id: int, current_user: User = Depends(get_current_active_user)):
    
    if current_user.isTutor:
        for speech in speech_feedback_data["speeches"]:
            if speech["speech_id"] == id:
                return speech

        raise HTTPException(
            status_code=404, detail=f'Speech with the corresponding ID not found'
        )
    else:
        return {"message": "You are not authorized to view specific speeches based on IDs"}



# adds one speech to the JSON file
@app.post('/speeches')
async def add_speech(speech: Speech, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        speech_dict = speech.dict()
        speech_found = False

        for speech in speech_feedback_data["speeches"]:
            if speech["speech_id"] == speech_dict["speech_id"]:
                speech_found = True
                return f'Speech ID {speech_dict["speech_id"]} already exists'

        if not speech_found:
            speech_feedback_data["speeches"].append(speech_dict)     # adds the new speech data to the JSON file
            with open(json_file, "w") as write_file:
                json.dump(speech_feedback_data, write_file, indent=2)          # Overwrites the previous file with the new JSON file

            return speech_dict

        raise HTTPException(
            status_code=404, detail=f'Speech not found'
        )
    else:
        return {"message": "You are not authorized as a tutor, you may not add new speeches to the database"}

# Updates one of the speeches (has to be an existing speech)
@app.put('/speeches')
async def update_speech(speech: Speech, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        speech_dict = speech.dict()
        speech_found = False
        for speech_idx, speech in enumerate(speech_feedback_data["speeches"]):
            if speech["speech_id"] == speech_dict["speech_id"]:
                speech_found = True
                speech_feedback_data["speeches"][speech_idx] = speech_dict

                with open(json_file, "w") as write_file:
                    json.dump(speech_feedback_data, write_file, indent=2)
                return "Updated"

        if not speech_found:
            return "Speech ID not found"
        raise HTTPException(
            status_code=404, detail="Speech not found"
        )
    else:
        return {"message": "You are not authorized as a tutor, you may not update speeches in the database"}

# Deletes a speech
@app.delete('/speeches/{speech_id}')
async def delete_speech(speech_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        speech_found = False
        for speech_idx, speech in enumerate(speech_feedback_data["speeches"]):
            if speech["speech_id"] == speech_id:
                speech_found = True
                speech_feedback_data["speeches"].pop(speech_idx)

                with open(json_file, "w") as write_file:
                    json.dump(speech_feedback_data, write_file, indent=2)
                return "Deleted"

        if not speech_found:
            return "Speech ID not found"
        raise HTTPException(
            status_code=404, detail=f"Speech not found"
        )
    else:
        return {"message": "You are not authorized as a tutor, you may not remove speeches from the database"}

# returns all feedback listed in the JSON data
@app.get('/feedback')
async def read_all_feedback(current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        return speech_feedback_data["feedback"]
    else:
        return {"message": "You are not authorized as a tutor, you may not view every feedback in the database"}

# Chooses a specific feedback based on speech ID
@app.get('/feedback/{speech_id}}')
async def read_feedback(speechID: int, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        for feedback in speech_feedback_data["feedback"]:
            if feedback["speech_id"] == speechID:
                return feedback

        raise HTTPException(
            status_code=404, detail=f"Feedback with the corresponding Speech ID not found"
        )
    else:
        return {"message": "You are not authorized as a tutor, you may view specific feedback based on ID"}

@app.post('/feedback')
async def generate_feedback(feedback: Feedback, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        feedback_dict = feedback.dict()
        speech_found = False
        feedback_found = False

        for speech in speech_feedback_data["speeches"]:
            if speech["speech_id"] == feedback_dict["speech_id"]:
                speech_found = True
                speech_used = speech

        if not speech_found:
            return f"Feedback for this Speech ID does not exist because there is no Speech with the corresponding ID"

        else:
            for feedback in speech_feedback_data["feedback"]:
                if feedback["speech_id"] == feedback_dict["speech_id"]:
                    feedback_found = True
                    return f"There is already Feedback for this Speech"

            if not feedback_found:
                # This segment rates the score and generates feedback
                feedback_dict["speech_id"] = speech_used["speech_id"]
                feedback_dict["student_id"] = speech_used["student_id"]
                feedback_dict["score"] = speech_used["argument_1_quality"] + \
                                        speech_used["argument_2_quality"] + \
                                        speech_used["substance_1_quality"] +  \
                                        speech_used["substance_2_quality"] + \
                                        speech_used["structure_quality"] + \
                                        speech_used["mannerism_confidence"] + \
                                        speech_used["mannerism_voice"]
                arr_aroi = switch_aoi(speech_used["argument_1_quality"], speech_used["argument_2_quality"],
                                    speech_used["substance_1_quality"], speech_used["substance_2_quality"],
                                    speech_used["structure_quality"], speech_used["mannerism_confidence"],
                                    speech_used["mannerism_voice"])
                feedback_dict["area_of_improvement_1"] = arr_aroi[0]
                feedback_dict["area_of_improvement_2"] = arr_aroi[1]
                feedback_dict["overall_feedback"] = switch_score(int(feedback_dict["score"]))

                speech_feedback_data["feedback"].append(feedback_dict)  # adds the feedback to the JSON data
                with open(json_file, "w") as write_file:
                    json.dump(speech_feedback_data, write_file, indent=2)

                return feedback_dict

        raise HTTPException(
            status_code=404,  detail="feedback not found"
        )
    else:
        return {"message": "You are not authorized as a tutor, you may not add new feeddback to the database"}


@app.put('/feedback')
async def update_feedback(feedback: Feedback, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        feedback_dict = feedback.dict()
        speech_found = False
        feedback_found = False

        for speech in speech_feedback_data["speeches"]:
            if speech["speech_id"] == feedback_dict["speech_id"]:
                speech_found = True
                speech_used = speech

        if not speech_found:
            return f"Feedback for this Speech ID cannot be updated because there is no Speech with the corresponding ID"

        else:
            for feedback in speech_feedback_data["feedback"]:
                if feedback["speech_id"] == feedback_dict["speech_id"]:
                    feedback_found = True

            if feedback_found:
                # This segment rates the score and generates feedback
                feedback_dict["speech_id"] = speech_used["speech_id"]
                feedback_dict["student_id"] = speech_used["student_id"]
                feedback_dict["score"] = speech_used["argument_1_quality"] + \
                                        speech_used["argument_2_quality"] + \
                                        speech_used["substance_1_quality"] + \
                                        speech_used["substance_2_quality"] + \
                                        speech_used["structure_quality"] + \
                                        speech_used["mannerism_confidence"] + \
                                        speech_used["mannerism_voice"]
                arr_aroi = switch_aoi(speech_used["argument_1_quality"], speech_used["argument_2_quality"],
                                    speech_used["substance_1_quality"], speech_used["substance_2_quality"],
                                    speech_used["structure_quality"], speech_used["mannerism_confidence"],
                                    speech_used["mannerism_voice"])
                feedback_dict["area_of_improvement_1"] = arr_aroi[0]
                feedback_dict["area_of_improvement_2"] = arr_aroi[1]
                feedback_dict["overall_feedback"] = switch_score(int(feedback_dict["score"]))

                speech_feedback_data["feedback"].append(feedback_dict)  # adds the feedback to the JSON data
                with open(json_file, "w") as write_file:
                    json.dump(speech_feedback_data, write_file, indent=2)

                return feedback_dict

            else:
                return "Feedback for this speech does not exist yet. Therefore, it cannot be updated"

        raise HTTPException(
            status_code=404, detail="feedback not found"
        )
    else:
        {"message": "You are not authorized as a tutor, you may not update feedback in tehe database"}

@app.delete('/feedback/{speech_id}')
async def delete_feedback(speech_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.isTutor:
        feedback_found = False
        for feedback_idx, feedback in enumerate(speech_feedback_data["feedback"]):
            if feedback["speech_id"] == speech_id:
                feedback_found = True
                speech_feedback_data["feedback"].pop(feedback_idx)

                with open(json_file, "w") as write_file:
                    json.dump(speech_feedback_data, write_file, indent=2)
                return "Deleted"

        if not feedback_found:
            return "Feedback does not exist for this speech"
        raise HTTPException(
            status_code=404, detail=f"Feedback not found"
        )
    else:
        return {"message": "You are not authorized as a tutor, you may not delete feedback from the database"}

# Get questions from Quizzma Service
@app.get("/getTestQuestions")
async def get_test(User = Depends(get_current_active_user)):
    all_questions = get_questions()

    skimmed_questions = all_questions[3]["question"]    # ID 3 adalah set yang dimilii critiquill

    debate_questions = { "questions": [

        ]
    }

    for i in range(0, len(skimmed_questions)):
        for question in skimmed_questions:
            if question["id"] == i+1:
                debate_questions["questions"].append({question["id"], question["question"]})

    return debate_questions


# Submit test and get score
@app.get("/takeTest")
async def take_test(answer1: str, answer2: str, answer3:str, answer4: str, answer5:str, answer6: str, User = Depends(get_current_active_user)):
    all_questions = get_questions()
    skimmed_questions = all_questions[3]["question"] # ID 3 adalah set yang dimilii critiquill
    score = 0
    answers = []
    scores = []
    for i in range(0, len(skimmed_questions)):
        for question in skimmed_questions:
            if question["id"] == i+1:
                answers.append(question["correct_answer"])
                scores.append(question["score_weight"])
    
    
    if answer1.upper() == answers[0]:
        score+= scores[0]

    if answer2.upper() == answers[1]:
        score+= scores[1]

    if answer3.upper() == answers[2]:
        score+= scores[2]
    
    if answer4.upper() == answers[3]:
        score+= scores[3]

    if answer5.upper() == answers[4]:
        score+= scores[4]
    
    if answer6.upper() == answers[5]:
        score+= scores[5]

    print(f"Your score is: {score}")
    return score




