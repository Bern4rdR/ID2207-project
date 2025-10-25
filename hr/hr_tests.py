from hr.crew_request import CrewRequest, Department

def test_create_hr():
    hr = CrewRequest("test request")
    assert hr != None

def test_hr_with_details():
    name="psr" 
    department=Department.Production
    description = "test descrintion"
    salary = 100
    fulltime = False
    hr = CrewRequest(name=name, department=department, description=description, salary=salary, fulltime=fulltime)
    assert hr.name == name
    assert hr.department == department
    assert hr.description == description
    assert hr.salary == salary
    assert hr.fulltime == fulltime

def test_hr_comment():
    comment = "asdfasdf"
    c2 = "hghghghgh"
    hr = CrewRequest("test")
    hr.add_comment(comment)
    assert hr.last_comment == comment
    hr.add_comment(c2)
    assert len(hr.get_comments()) == 2

def test_hr_approve():
    hr = CrewRequest("app")
    h2 = CrewRequest("unapp")
    hr.approve()
    assert hr.approved
    assert not h2.approved
