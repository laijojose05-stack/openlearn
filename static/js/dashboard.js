function loadSection(section) {
    let main = document.getElementById("main");

    if (section === "home") {
        main.innerHTML = "<h2 class='fade'>Welcome Back!</h2>";
    }

    if (section === "teachers") {
        main.innerHTML = `
        <h2>Manage Teachers</h2>
        <form>
            <input placeholder="Name">
            <input placeholder="Email">
            <input placeholder="Password">
            <select>
                <option>CE</option>
                <option>CT</option>
                <option>ECE</option>
                <option>EEE</option>
                <option>ME</option>
            </select>
            <button>Add Teacher</button>
        </form>`;
    }

    if (section === "assign") {
        main.innerHTML = "<h2>Assign Teacher to Branch</h2>";
    }

    if (section === "approve") {
        main.innerHTML = "<h2>Approve Students</h2>";
    }

    if (section === "notes") {
        main.innerHTML = `
        <h2>Upload Notes</h2>
        <form enctype="multipart/form-data">
            <input type="text" placeholder="Title">
            <input type="file">
            <button>Upload</button>
        </form>`;
    }

    if (section === "updates") {
        main.innerHTML = `
        <h2>Notifications</h2>
        <textarea rows="4" placeholder="Message"></textarea>
        <button>Add</button>`;
    }

    if (section === "attendance") {
        main.innerHTML = "<h2>Mark Attendance</h2>";
    }
}
