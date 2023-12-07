from pydantic import BaseModel
import datetime

class Speech(BaseModel):
    speech_id: int
    student_id: int
    student_name: str
    speech_topic: str
    speech_date: str
    argument_1: str
    argument_1_quality: int
    argument_2: str
    argument_2_quality: int
    substance_1: str
    substance_1_quality: int
    substance_2: str
    substance_2_quality: int
    structure_type: str
    structure_quality: int
    mannerism_confidence: int
    mannerism_voice: int

    # def __init__(self):
    #     self.student_id = int(input("Input student ID: "))
    #     self.student_name = input("Input student name: ")
    #     self.speech_topic = input("Input motion topic: ")
    #     date = datetime.datetime.now()
    #     self.speech_date = str(date)
    #     self.argument_1 = input("Input the first argument: ")
    #     self.argument_1_quality = int(input("Argument 1 quality (1-5): "))
    #     self.argument_2 = input("Input the second argument: ")
    #     self.argument_2_quality = int(input("Argument 2 quality (1-5): "))
    #     self.substance_1 = input("Input the substance of the first argument: ")
    #     self.substance_1_quality = int(input("Substance 1 quality (1-5): "))
    #     self.substance_2 = input("Input the substance of the first argument: ")
    #     self.substance_2_quality = int(input("Substance 2 quality (1-5): "))
    #     self.structure_type = (input("Input the structure type (Unstructured/semi-structured/signposted: ")).lower()
    #     self.structure_quality = int(input("Structure quality (1-5): "))
    #     self.mannerism_confidence = int(input("Input speech confidence (1-5): "))
    #     self.mannerism_voice = int(input("Input speech mannerism (1-5): "))

class Feedback(BaseModel):
    speech_id: int


def switch_score(score):
    if score > 30:
        return "Fantastic Speech! You only need to work on the details. Keep up the good work"
    elif score > 24 and score <= 30:
        return "Great Speech! You have solid fundamentals and good execution. Work on taking it to the next level"
    elif score > 19 and score <=24:
        return "Solid Speech! Your fundamentals are good but some polishment is needed. Refine your fundamentals"
    elif score >10 and score <=19:
        return "You need to re-evaluate the basics and fundamentals, focus on being concise and addressing the right issues"
    else:
        return "Your speech needs a fundamental revamn, lots of key areas were missing and/or could use evaluation"

def switch_aoi(arg1, arg2, sub1, sub2, structure, conf, voi):
    arr_result = []
    # phase 1 of selection
    if arg1 < 3:
        arr_result.append("Work on analyzing and improving your first argument")
        arg1 = 100
    elif arg2 < 3:
        arr_result.append("Work on analyzing and improving your second argument")
        arg2 = 100
    elif sub1 < 3:
        arr_result.append("Work on adding weight and adding substance to your first argument")
        sub1 = 100
    elif sub2 < 3:
        arr_result.append("Work on adding weight and adding substance to your second argument")
        sub2 = 100
    elif structure < 3:
        arr_result.append("Format your speech so that it becomes tidier, make sure that your speech is easy to follow")
        structure = 100
    elif conf<3:
        arr_result.append("Be more confident and assertive when delivering your speech")
        conf = 100
    elif voi<3:
        arr_result.append("Improve the tone, tempo, and flow of your voice when delivering your speech")
        voi=100
    else:
        if arg1 < 4:
            arr_result.append("Work on analyzing and improving your first argument")
            arg1 = 100
        elif arg2 < 4:
            arr_result.append("Work on analyzing and improving your second argument")
            arg2 = 100
        elif sub1 < 4:
            arr_result.append("Work on adding weight and adding substance to your first argument")
            sub1 = 100
        elif sub2 < 4:
            arr_result.append("Work on adding weight adding substance to your second argument")
            sub2= 100
        elif structure < 5:
            arr_result.append("Format your speech so that it becomes tidier, make sure that your speech is easy to follow")
            structure=100
        elif conf < 5:
            arr_result.append("Be more confident and assertive when delivering your speech")
            conf = 100
        else:
            arr_result.append("Improve the tone, tempo, and flow of your voice when delivering your speech")
            voi = 100

    # phase 2 of selection
    if arg1 < 3:
        arr_result.append("Work on analyzing and improving your first argument")
        arg1 = 100
    elif arg2 < 3:
        arr_result.append("Work on analyzing and improving your second argument")
        arg2 = 100
    elif sub1 < 3:
        arr_result.append("Work on adding weight and adding substance to your first argument")
        sub1 = 100
    elif sub2 < 3:
        arr_result.append("Work on adding weight adding substance to your second argument")
        sub2 = 100
    elif structure < 3:
        arr_result.append("Format your speech so that it becomes tidier, make sure that your speech is easy to follow")
        structure = 100
    elif conf<3:
        arr_result.append("Be more confident and assertive when delivering your speech")
        conf = 100
    elif voi<3:
        arr_result.append("Improve the tone, tempo, and flow of your voice when delivering your speech")
        voi=100
    else:
        if arg1 < 4:
            arr_result.append("Work on analyzing and improving your first argument")
            arg1 = 100
        elif arg2 < 4:
            arr_result.append("Work on analyzing and improving your second argument")
            arg2 = 100
        elif sub1 < 4:
            arr_result.append("Work on adding weight and adding substance to your first argument")
            sub1 = 100
        elif sub2 < 4:
            arr_result.append("Work on adding weight adding substance to your second argument")
            sub2= 100
        elif structure < 5:
            arr_result.append("Format your speech so that it becomes tidier, make sure that your speech is easy to follow")
            structure=100
        elif conf < 5:
            arr_result.append("Be more confident and assertive when delivering your speech")
            conf = 100
        else:
            arr_result.append("Improve the tone, tempo, and flow of your voice when delivering your speech")
            voi = 100

    return arr_result





