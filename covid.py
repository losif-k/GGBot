from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
import xmltodict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def getdatancov():
    data = dict(xmltodict.parse(requests.get('http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson', params={
            'serviceKey': os.getenv('SERVICE_KEY'),
            'startCreateDt': f'20{datetime.now().strftime("%y%m%d")}'}).content)['response']['body']['items']['item'])
    p_data = {
        '기준일': data['stateDt'], # 기준일
        '확진자 수': data['decideCnt'], # 확진자 수
        '격리해제 수': data['clearCnt'], # 격리해제 수
        '검사진행 수': data['examCnt'], # 검사진행 수
        '사망자 수': data['deathCnt'], # 사망자 수
        '치료중 환자 수': data['careCnt'], # 치료중 환자 수
        '결과 음성 수': data['resutlNegCnt'], # 결과 음성 수
        '누적 검사 수': data['accExamCnt'], # 누적 검사 수
        '누적 검사 완료 수 ': data['accExamCompCnt'] # 누적 검사 완료 수
    }
    return [p_data['기준일'], p_data['확진자 수'], p_data['격리해제 수'], p_data['검사진행 수'], p_data['사망자 수']]