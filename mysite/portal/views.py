from django.shortcuts import render
from django.http import HttpResponse
from config import ACCESS_TOKEN, API_KEY
from endpoints import HOST, SURVEY_LIST_ENDPOINT, SURVEY_DETAILS_ENDPOINT, USER_DETAILS_ENDPOINT, RESPONDENT_LIST_ENDPOINT, GET_RESPONSES_ENDPOINT
from .models import Users
import requests
import json

def index(request):
    
    client = requests.session()
    client.headers = {
        "Authorization": "bearer %s" % ACCESS_TOKEN
    ,
        "Content-Type": "application/json",
    }
    client.params = {
        "api_key": API_KEY
    }
    uri = "%s%s" % (HOST, SURVEY_DETAILS_ENDPOINT)
    data = {"survey_id" : "76003826"}
    response = client.post(uri, data=json.dumps(data))
    survey_details = response.json()
  
    uri = "%s%s" % (HOST, RESPONDENT_LIST_ENDPOINT)
    data = {"survey_id" : "76003826"}
    response = client.post(uri, data=json.dumps(data))
    respondent_result = response.json()
    respondent_list = []
    for a in respondent_result['data']['respondents']:
    	respondent_list.append(a['respondent_id'])

    uri = "%s%s" % (HOST, GET_RESPONSES_ENDPOINT)
    data = {"survey_id" : "76003826" , "respondent_ids" : respondent_list}
    response = client.post(uri, data=json.dumps(data))
    responses_received = response.json()
    
    lis = []
    temp_ques_dict = {}

    for page in survey_details['data']['pages']:
    	
    	for question in page['questions']:
    		question_id = question['question_id']
    		question_text = question['heading']
    		temp_ans_list = []
    		for answer in question['answers']:
    			temp_ans_list.append({"answer_id" : answer['answer_id'] , "answer_text" : answer['text'], 
    									"marked_yes" : 0})
    		temp_ques_dict.update({"question_id" : question_id , "question_text" : question_text, 
    									 "answers" : temp_ans_list })
    		lis.append(temp_ques_dict)
    		temp_ques_dict = {}
    new_lis = sorted(lis, key=lambda k: k['question_id'])

    response_list_final = []
    for respondent in responses_received['data']:
    	for question in respondent['questions']:
    		response_list_final.append({"question_id" : question['question_id'] , "answer_id" : question['answers'][0]['row']})

    newlist = sorted(response_list_final, key=lambda k: k['question_id'])		
    

    final_dict = {}
    for a in newlist:
    	if a['question_id'] in final_dict:
    		final_dict[a['question_id']].append(a['answer_id'])
    	else:
    		final_dict.update({a['question_id'] : [a['answer_id']]})

    for a in new_lis:
    	for b in final_dict[a['question_id']]:
    		for c in  a['answers']:
    			if c['answer_id'] == b :
    				c['marked_yes'] = c['marked_yes'] + 1
    				break

    
    import plotly.plotly as py
    import plotly.graph_objs as go

    age= [a['answer_text'] for a in new_lis[1]['answers']]
    marked= [a['marked_yes'] for a in new_lis[1]['answers']]
    # print pop
    data = [
        go.Bar(
            x=age,
            y=marked
        )
    ]
    plot_url = py.plot(data, filename='basic-bar')
    final_url = plot_url + ".embed?link=false&modebar=false&autosize=True"
    print final_url
    lol = {"title" : final_url}
    return render(request, 'portal/index.html', lol)

    # b6nnuuh9ab