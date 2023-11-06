from fastapi import FastAPI, HTTPException
import json
from feedback_classes import *


json_file = "speeches_and_feedback.json"

with open(json_file, "r") as read_file:
    speech_feedback_data = json.load(read_file)

app = FastAPI()

# Home
@app.get('/')
async def read_home():
    return {"message": "Welcome to Critiquill Services"}

# returns all speeches listed in the JSON data
@app.get('/speeches')
async def read_all_speeches():
    return speech_feedback_data['speeches']

# Gets all speeches made by a certain student
@app.get('/speeches/students/{student_id}')
async def read_speech_student_id(student_id: int):
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

# Chooses a specific speech ID
@app.get('/speeches/{speech_id}')
async def read_speech_id(id: int):
    for speech in speech_feedback_data["speeches"]:
        if speech["speech_id"] == id:
            return speech

    raise HTTPException(
        status_code=404, detail=f'Speech with the corresponding ID not found'
    )



# adds one speech to the JSON file
@app.post('/speeches')
async def add_speech(speech: Speech):
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

# Updates one of the speeches (has to be an existing speech)
@app.put('/speeches')
async def update_speech(speech: Speech):
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

# Deletes a speech
@app.delete('/speeches/{speech_id}')
async def delete_speech(speech_id: int):
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

# returns all feedback listed in the JSON data
@app.get('/feedback')
async def read_all_feedback():
    return speech_feedback_data["feedback"]

# Chooses a specific feedback based on speech ID
@app.get('/feedback/{speech_id}}')
async def read_feedback(speechID: int):
    for feedback in speech_feedback_data["feedback"]:
        if feedback["speech_id"] == speechID:
            return feedback

    raise HTTPException(
        status_code=404, detail=f"Feedback with the corresponding Speech ID not found"
    )

@app.post('/feedback')
async def generate_feedback(feedback: Feedback):
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

@app.put('/feedback')
async def update_feedback(feedback: Feedback):
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

@app.delete('/feedback/{speech_id}')
async def delete_feedback(speech_id: int):
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





