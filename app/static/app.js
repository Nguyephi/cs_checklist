
const token = (window.location.search.split("=")[0] === "?api_key") ? window.location.search.split("#_=_")[0] : null;
const URL = 'https://127.0.0.1:5000'
const current_user = { token: '' }


async function storeToken() {
    const accessToken = (window.location.search.split("=")[0] === "?api_key") ? window.location.search.split("#_=_")[0] : null;
    if (accessToken) {
        sessionStorage.setItem("token", accessToken.replace('?api_key=', ''));
        current_user.token = accessToken.replace('?api_key=', '')
    }

    const existingToken = sessionStorage.getItem('token');
    if (existingToken) {
        current_user.token = existingToken.replace('?api_key=', '')
    };
}
storeToken()


let id = 1
function addSubTask() {
    let subTask = document.getElementById(`form-subTask-${id}`).value
    if (subTask.length > 0) {
        id += 1
        document.getElementById(`new-subTask-${id - 1}`).innerHTML = `
        <form method='POST' class='d-flex justify-content-between'>   
            <div class="md-form my-0">
                <label style='color:red' for="form-subTask-${id}">Sub Task</label>
                <input name='subTask' type="text", id="form-subTask-${id}", class='todoInput form-control validate' />
            </div>
        </form>
        <div id="new-subTask-${id}"></div>
        `
    }
}

async function deleteTodo(id) {
    await fetch(`${URL}/delete/${id}`, {
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        }),
        method: 'DELETE'
    })
    document.getElementById(`todo-${id}`).setAttribute('style', 'display: none !important')
    document.getElementById(`todo-${id}`).innerHTML = ''
}

async function deleteSubTodo(id) {
    await fetch(`${URL}/deletesub/${id}`, {
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        }),
        method: 'DELETE'
    })
    document.getElementById(`subTodo-${id}`).setAttribute('style', 'display: none !important')
    document.getElementById(`subTodo-${id}`).innerHTML = ''
}

async function editTodo(id) {
    const res = await fetch(`${URL}/edit/${id}`, {
        method: 'GET',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        })
    })
    const data = await res.json()
    document.getElementById(`todo-${id}`).innerHTML = `
    <form method='POST' class='d-flex justify-content-between'>
        <div class="md-form my-0" style='width: 85%;'>
            <input value='${data.todo}' type="text", id="form-name-${id}", class='mb-0 todoInput form-control validate' />
        </div>
        <div class='d-flex'>
        <button type="button" onclick="updateTodo(${id}, document.getElementById('form-name-${id}').value)" class='edit'><small>update</small></button>
        <button type='button' onclick='deleteTodo(${id})' class='delete'><small>delete</small></button>
        </div>
    </form>
    `
}

async function editSubTodo(id) {
    const res = await fetch(`${URL}/editsub/${id}`, {
        method: 'GET',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        })
    })
    const data = await res.json()
    document.getElementById(`subTodo-${id}`).innerHTML = `
    <form method='POST' class='d-flex justify-content-between'>
        <div class="md-form my-0" style='width: 85%;'>
            <input value='${data.todo}' type="text", id="form-name-${id}", class='mb-0 todoInput form-control validate' />
        </div>
        <div class='d-flex'>
        <button type="button" onclick="updateSubTodo(${id}, document.getElementById('form-name-${id}').value)" class='edit'><small>update</small></button>
        <button type='button' onclick='deleteSubTodo(${id})' class='delete'><small>delete</small></button>
        </div>
    </form>
    `
}

async function updateTodo(id, todo) {
    const res = await fetch(`${URL}/update/${id}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        }),
        body: JSON.stringify({
            'todo': todo
        })
    })
    let task = ''
    const data = await res.json()
    task = data.todo
    task = task.charAt(0).toUpperCase() + task.slice(1);
    console.log(task);
    document.getElementById(`todo-${id}`).innerHTML = `
        <div class='d-flex justify-content-between'>
            <div class='mb-2'>
                <form method='POST' class="custom-control custom-checkbox">
                    <input onclick='todoDone(${id})' type="checkbox" class="custom-control-input"
                        id="checkbox-${id}">
                    <label class="custom-control-label h5-responsive"
                        for="checkbox-${id}">${task}</label>
                </form>
            </div>
            <div class='d-flex'>
            <button onclick="editTodo(${id})" class='edit'><small>edit</small></button>
                <button onclick="deleteTodo(${id})" class='delete'><small>delete</small></button>
            </div>
        </div>
    `
}

async function updateSubTodo(id, todo) {
    const res = await fetch(`${URL}/updatesub/${id}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        }),
        body: JSON.stringify({
            'todo': todo
        })
    })
    let task = ''
    const data = await res.json()
    task = data.todo
    task = task.charAt(0).toUpperCase() + task.slice(1);
    document.getElementById(`subTodo-${id}`).innerHTML = `
        <div class='d-flex justify-content-between'>
            <div class='mb-2'>
                <form method='POST' class="custom-control custom-checkbox">
                    <input onclick='subTodoDone(${id})' type="checkbox" class="custom-control-input"
                        id="sub-checkbox-${id}">
                    <label class="custom-control-label h5-responsive"
                        for="sub-checkbox-${id}">${task}</label>
                </form>
            </div>
            <div class='d-flex'>
            <button onclick="editSubTodo(${id})" class='edit'><small>edit</small></button>
                <button onclick="deleteSubTodo(${id})" class='delete'><small>delete</small></button>
            </div>
        </div>
    `
}

async function todoDone(id) {
    await fetch(`${URL}/isdone/${id}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        })
    })
}

async function isTodoDone() {
    const response = await fetch(`${URL}/checklistdata`, {
        method: 'GET',
        headers: new Headers({
            "Content-Type": "application/json",
            "Authorization": `Token ${current_user.token}`
        })
    })
    const data = await response.json()

    const todos = data.checklist.map(todo => {
        console.log(todo)
        if (todo.is_done == true && todo.todo_id) {
            document.getElementById(`checkbox-${todo.todo_id}`).checked = true
        } else if (todo.is_done == true && todo.sub_todo_id) {
            document.getElementById(`sub-checkbox-${todo.sub_todo_id}`).checked = true
        }
        // else {
        //     document.getElementById(`checkbox-${todo.todo_id}`).checked = false
        //     document.getElementById(`sub-checkbox-${todo.sub_todo_id}`).checked = false
        // }
    })
    return todos
}
isTodoDone()

async function subTodoDone(id) {
    await fetch(`${URL}/issubdone/${id}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Token ${current_user.token}`
        })
    })
}

