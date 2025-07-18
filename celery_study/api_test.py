import time
import requests


BASE_URL = "http://localhost:8000"

def test_task_1(a:int, b:int):
    url = f"{BASE_URL}/add/{a}/{b}"
    res = requests.get(url)
    print(res.json())
    return res.json()


def get_result(task_id:str):
    url = f"{BASE_URL}/result/{task_id}"
    res = requests.get(url)
    print(res.json())
    return res.json()


if __name__ == "__main__":
    res = test_task_1(2,5)
    print("sleep 6 sec")
    time.sleep(6)
    res2 = get_result(res['task_id'])
    print("sleep 6 sec")
    time.sleep(6)
    res2 = get_result(res['task_id'])
    
    
    
    