import hashlib
import sqlite3
import os

from flask import Flask, request, session, render_template

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

app.secret_key = "akshnex_secret_key_2026"
def find_best_professional(service, problem, location):
    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            employee_id,
            employee_name,
            role,
            skills,
            location,
            experience,
            rating,
            availability
        FROM employees
        WHERE availability = 'Available'
        """
    )

    professionals = cursor.fetchall()
    connection.close()

    service_text = (service or "").lower()
    problem_text = (problem or "").lower()
    location_text = (location or "").lower()

    best_professional = None
    best_score = -1

    for professional in professionals:

        employee_id = professional[0]
        employee_name = professional[1]
        role = professional[2]
        skills = (professional[3] or "").lower()
        professional_location = (professional[4] or "").lower()
        experience = professional[5] or 0
        rating = professional[6] or 0

        score = 0
        # Service match
        if service_text and service_text in skills:
            score += 40
        else:
            continue

        # Role match
        role_text = role.lower()

        if "ac" in service_text and "ac technician" in role_text:
            score += 30

        elif "electrical" in service_text and "electrical technician" in role_text:
            score += 30
              
        # Problem/skill match
        problem_words = problem_text.replace(",", " ").split()

        for word in problem_words:
            if len(word) > 2 and word in skills:
                score += 5

        # Location match
        if location_text and location_text in professional_location:
            score += 25

        # Experience
        score += min(experience, 10)

        # Rating
        score += rating * 2

        if score > best_score:
            best_score = score

            best_professional = {
                "employee_id": employee_id,
                "employee_name": employee_name,
                "role": role,
                "score": round(score, 1)
            }

    return best_professional
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/services", methods=["GET", "POST"])
def services():

    if request.method == "POST":

        customer_name = request.form.get("customer_name", "").strip()
        service = request.form.get("service", "").strip()
        problem = request.form.get("problem", "").strip()
        location = request.form.get("location", "").strip()

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT request_id FROM service_requests ORDER BY rowid DESC LIMIT 1"
        )

        last_request = cursor.fetchone()

        if last_request:
            number = int(last_request[0].split("-")[1]) + 1
        else:
            number = 1001

        request_id = f"AN-{number}"

        cursor.execute(
            """
            INSERT INTO service_requests
            (
                request_id,
                customer_name,
                service,
                problem,
                location,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                customer_name,
                service,
                problem,
                location,
                "Submitted"
            )
        )
        # Automatically find the best professional
        best_professional = find_best_professional(
            service,
            problem,
            location
        )

        if best_professional:
            professional_id = best_professional["employee_id"]
            professional_name = best_professional["employee_name"]

            cursor.execute(
                """
                UPDATE service_requests
                SET professional_id = ?, professional_name = ?, status = ?
                WHERE request_id = ?
                """,
                (
                    professional_id,
                    professional_name,
                    "Assigned",
                    request_id
                )
            )
        connection.commit()
        connection.close()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Service Request Submitted</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f5f7fb;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }}

                .box {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }}

                h1 {{
                    color: #222;
                }}

                .id {{
                    font-size: 28px;
                    font-weight: bold;
                    margin: 20px 0;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 20px;
                    background: #222;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }}
            </style>
        </head>

        <body>

            <div class="box">

                <h1>Application Submitted Successfully!</h1>

                <p>Your service request has been created.</p>

                <div class="id">
                    {request_id}
                </div>

                <p>Please save this Request ID to track your service.</p>

                <a href="/track">
                    Track Service Request
                </a>

            </div>

        </body>
        </html>
        """

    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Book a Service</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 40px;
            }

            .container {
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 35px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }

            h1 {
                margin-bottom: 25px;
            }

            label {
                display: block;
                margin-top: 15px;
                margin-bottom: 6px;
                font-weight: bold;
            }

            input,
            select,
            textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-sizing: border-box;
            }

            textarea {
                min-height: 100px;
            }

            button {
                margin-top: 25px;
                width: 100%;
                padding: 14px;
                background: #222;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }

            button:hover {
                background: #444;
            }
        </style>

    </head>

    <body>

        <div class="container">

            <h1>Book a Service</h1>

            <form method="POST">

                <label>Customer Name</label>
                <input
                    type="text"
                    name="customer_name"
                    required
                >

                <label>Service</label>

                <select name="service" required>

                    <option value="">
                        Select Service
                    </option>

                    <option value="AC Repair">
                        AC Repair
                    </option>

                    <option value="Electrical Repair">
                        Electrical Repair
                    </option>

                    <option value="Plumbing">
                        Plumbing
                    </option>

                    <option value="Appliance Repair">
                        Appliance Repair
                    </option>

                </select>

                <label>Problem</label>

                <textarea
                    name="problem"
                    placeholder="Describe your problem"
                    required
                ></textarea>

                <label>Location</label>

                <input
                    type="text"
                    name="location"
                    placeholder="Enter your city/location"
                    required
                >

                <button type="submit">
                    Submit Service Request
                </button>

            </form>

        </div>

    </body>

    </html>
    """

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Book a Service | AkshNex</title>

        <style>

            

    <head>

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Professionals | AkshNex</title>

        <style>

            * {
            box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            body {
                margin: 0;
                background: #f6f8fc;
                color: #172033;
            }

            header {
                background: white;
                padding: 18px 7%;
                border-bottom: 1px solid #e7e9ef;
            }

            .logo {
                font-size: 28px;
                font-weight: 800;
            }

            .logo span {
                color: #5b5ce2;
            }

            .container {
                max-width: 1000px;
                margin: 35px auto;
                padding: 20px;
            }

            .title h1 {
                margin-bottom: 8px;
            }

            .title p {
                color: #697386;
            }

            .search {
                background: white;
                padding: 20px;
                border-radius: 18px;
                margin: 25px 0;
                border: 1px solid #e5e7eb;
            }

            .search input,
            .search select {
                width: 100%;
                padding: 13px;
                margin-top: 8px;
                margin-bottom: 15px;
                border: 1px solid #d9deea;
                border-radius: 10px;
                font-size: 15px;
            }

            .search button {
                width: 100%;
                padding: 14px;
                background: #5b5ce2;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }

            .smart-match {
                background: linear-gradient(135deg, #5b5ce2, #7b61ff);
                color: white;
                padding: 25px;
                border-radius: 20px;
                margin: 25px 0;
            }

            .smart-match h2 {
                margin-top: 0;
            }

            .professional {
                background: white;
                padding: 25px;
                border-radius: 20px;
                margin-bottom: 18px;
                border: 1px solid #e5e7eb;
            }

            .top {
                display: flex;
                justify-content: space-between;
                gap: 15px;
            }

            .name {
                font-size: 20px;
                font-weight: bold;
            }

            .rating {
                color: #f59e0b;
                font-weight: bold;
            }

            .speciality {
                color: #5b5ce2;
                font-weight: bold;
                margin-top: 7px;
            }

            .details {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 18px 0;
            }

            .tag {
                background: #f3f5f9;
                padding: 8px 11px;
                border-radius: 9px;
                font-size: 14px;
            }

            .available {
                color: #16834b;
            }

            .match-score {
                color: #5b5ce2;
                font-weight: bold;
                margin: 15px 0;
            }
.match-reason {
    margin-top: 10px;
    padding: 10px 12px;
    background: #f3f5f9;
    border-radius: 8px;
    color: #596273;
    font-size: 13px;
}
            .request {
    display: block;
    width: 100%;
    padding: 13px;
    background: #172033;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    box-sizing: border-box;
}
            .back {
                display: block;
                text-align: center;
                margin-top: 25px;
                color: #5b5ce2;
                text-decoration: none;
            }

        </style>

    </head>

    <body>

        <header>

            <div class="logo">
                Aksh<span>Nex</span>
            </div>

        </header>

        <div class="container">

            <div class="title">

                <h1>Find the Right Professional</h1>

                <p>
                    Search yourself or let AkshNex find the most suitable
                    professional for your job.
                </p>

            </div>

            <div class="search">

                <label>
                    What service do you need?
                </label>

                <select id="service">

                    <option value="">Select service</option>
                    <option value="AC Repair">AC Repair</option>
                    <option value="Washing Machine Repair">
                        Washing Machine Repair
                    </option>
                    <option value="Refrigerator Repair">
                        Refrigerator Repair
                    </option>
                    <option value="Electrical Work">
                        Electrical Work
                    </option>
                    <option value="Plumbing">Plumbing</option>
                    <option value="Vehicle Service">
                        Vehicle Service
                    </option>

                </select>
                 <label>
    What problem are you facing?
</label>

<select id="problem">

    <option value="">Select problem</option>

    <option value="Cooling Repair">
        ❄️ Cooling Problem
    </option>

    <option value="Gas Leakage">
        🛠️ Gas Leakage
    </option>

    <option value="Electrical AC Repair">
        ⚡ Electrical Problem
    </option>

    <option value="Compressor Repair">
        🔧 Compressor Problem
    </option>

    <option value="General AC Repair">
        🔍 General AC Service
    </option>

</select>

                <label>
                    Your location
                </label>

                <input
                    id="location"
                    type="text"
                    placeholder="Enter your location"
                >

                <button
                    type="button"
                    onclick="findProfessionals()"
                >
                    🔎 Find Professionals
                </button>

            </div>

            <div class="smart-match">

                <h2>
                    🧠 AkshNex Smart Match
                </h2>

                <p>
                    AkshNex can compare skill, experience, ratings,
                    availability, location and previous similar jobs
                    to suggest suitable professionals.
                </p>

            </div>

            <h2>
                Recommended Professionals
            </h2>

            <div
                class="professional"
    data-service="AC Repair"
    data-skills="Cooling Repair,Gas Leakage,Electrical AC Repair"
    data-experience="8"
    data-similar-jobs="312"
    data-rating="4.8"
    data-distance="2.1"
    data-availability="available"
>
                <div class="top">

                    <div>

                        <div class="name">
                            Ravi Kumar
                        </div>

                        <div class="speciality">
                            ❄️ AC Specialist
                        </div>

                    </div>

                    <div class="rating">
                        ⭐ 4.8
                    </div>

                </div>

                <div class="match-score">
                    AkshNex Match: 96%
                </div>

                <div class="details">

                    <div class="tag">
                        🛠️ 8 years experience
                    </div>

                    <div class="tag">
                        ✅ 312 similar jobs
                    </div>

                    <div class="tag">
                        📍 2.1 km
                    </div>

                    <div class="tag available">
                        🟢 Available now
                    </div>

                </div>

            <a href="/services" class="request">
    📩 Request Service
</a>
            </div>

            

            <div
                class="professional"
    data-service="AC Repair"
    data-skills="Cooling Repair,Compressor Repair,Gas Leakage"
    data-experience="6"
    data-similar-jobs="185"
    data-rating="4.7"
    data-distance="3.4"
    data-availability="available"
>


                <div class="top">

                    <div>

                        <div class="name">
                            Suresh Kumar
                        </div>

                        <div class="speciality">
                            ❄️ AC Technician
                        </div>

                    </div>

                    <div class="rating">
                        ⭐ 4.7
                    </div>

                </div>

                <div class="match-score">
                    AkshNex Match: 91%
                </div>

                <div class="details">

                    <div class="tag">
                        🛠️ 6 years experience
                    </div>

                    <div class="tag">
                        ✅ 185 similar jobs
                    </div>

                    <div class="tag">
                        📍 3.4 km
                    </div>

                    <div class="tag available">
                        🟢 Available now
                    </div>

                </div>

                
    <a href="/services" class="request">
    📩 Request Service
</a>
            </div>

            <div
                class="professional"
    data-service="AC Repair"
    data-skills="Electrical AC Repair,Compressor Repair,General AC Repair"
    data-experience="9"
    data-similar-jobs="521"
    data-rating="4.9"
    data-distance="5.2"
    data-availability="available"
>

                <div class="top">

                    <div>

                        <div class="name">
                            Arun Reddy
                        </div>

                        <div class="speciality">
                            🔧 AC & Appliance Specialist
                        </div>

                    </div>

                    <div class="rating">
                        ⭐ 4.9
                    </div>

                </div>

                <div class="match-score">
                    AkshNex Match: 88%
                </div>

                <div class="details">

                    <div class="tag">
                        🛠️ 9 years experience
                    </div>

                    <div class="tag">
                        ✅ 521 similar jobs
                    </div>

                    <div class="tag">
                        📍 5.2 km
                    </div>

                    <div class="tag available">
                        🟢 Available now
                    </div>

                </div>

               <a href="/services" class="request">
    📩 Request Service
</a>
            </div>

            <a class="back" href="/">
                ← Back to AkshNex
            </a>

        </div>

        <script>
        
            function findProfessionals() {

    const service = document.getElementById("service").value;
    const problem = document.getElementById("problem").value;
    const location = document.getElementById("location").value.trim();

    if (service === "") {
        alert("Please select a service.");
        return;
    }

    if (problem === "") {
        alert("Please select the problem.");
        return;
    }

    if (location === "") {
        alert("Please enter your location.");
        return;
    }

    const professionals =
        Array.from(document.querySelectorAll(".professional"));

    let matches = [];

    professionals.forEach(function(professional) {

        const professionalService =
            professional.getAttribute("data-service");

        const skills =
            professional.getAttribute("data-skills") || "";

        const experience =
            Number(professional.getAttribute("data-experience") || 0);

        const similarJobs =
            Number(professional.getAttribute("data-similar-jobs") || 0);

        const rating =
            Number(professional.getAttribute("data-rating") || 0);

        const distance =
            Number(professional.getAttribute("data-distance") || 0);

        const availability =
            professional.getAttribute("data-availability") || "";

        const serviceMatch =
            professionalService === service;

        const skillMatch =
            skills.toLowerCase().includes(problem.toLowerCase());

        if (!serviceMatch || !skillMatch) {
            professional.style.display = "none";
            return;
        }

        const experienceScore =
            Math.min(experience / 10, 1) * 15;

        const similarJobsScore =
            Math.min(similarJobs / 500, 1) * 15;

        const ratingScore =
            (rating / 5) * 10;

        const distanceScore =
            Math.max(0, 1 - distance / 10) * 5;

        const availabilityScore =
            availability.toLowerCase() === "available"
                ? 5
                : 0;

        const totalScore =
            50 +
            experienceScore +
            similarJobsScore +
            ratingScore +
            distanceScore +
            availabilityScore;

        matches.push({
            element: professional,
            score: Math.round(totalScore)
        });
    });

    if (matches.length === 0) {

        alert("No matching professionals found.");
        return;
    }

    matches.sort(function(a, b) {
        return b.score - a.score;
    });

    matches.forEach(function(match, index) {

        const professional = match.element;

        professional.style.display = "block";

        const scoreElement =
            professional.querySelector(".match-score");

        if (scoreElement) {
            scoreElement.textContent =
                "AkshNex Match: " + match.score + "%";
        }

        let rankElement =
            professional.querySelector(".akshnex-rank");

        if (!rankElement) {
            rankElement = document.createElement("div");
            rankElement.className = "akshnex-rank";
            professional.insertBefore(
                rankElement,
                professional.firstChild
            );
        }

        rankElement.textContent =
            "🏆 Rank #" + (index + 1);
            const reasonElement =
    professional.querySelector(".match-reason");

if (!reasonElement) {

    const reason = document.createElement("div");

    reason.className = "match-reason";

    let reasons = [];

if (experience >= 8) {
    reasons.push("High experience");
} else if (experience >= 5) {
    reasons.push("Good experience");
}

if (similarJobs >= 300) {
    reasons.push("Many similar jobs");
} else if (similarJobs >= 150) {
    reasons.push("Good job history");
}

if (rating >= 4.8) {
    reasons.push("Excellent rating");
} else if (rating >= 4.5) {
    reasons.push("Good rating");
}

if (distance <= 3) {
    reasons.push("Nearby");
}

if (availability.toLowerCase() === "available") {
    reasons.push("Available now");
}

reason.textContent =
    "✓ " + reasons.join("  ✓ ");
    professional.appendChild(reason);
}
    });

    alert(
        "AkshNex found " + matches.length + " professional(s) matching your problem." );
}
function requestService(button) {

    const card = button.closest(".professional");

    const name = card
        .querySelector(".name")
        .textContent
        .trim();

    alert(
        "REQUEST SERVICE\n\n" +
        "Professional: " + name
    );
}
        </script>
        
    </body>
    </html>
    """ 
@app.route("/track", methods=["GET", "POST"])
def track():

    request_data = None
    error = None

    if request.method == "POST":

        request_id = request.form.get("request_id", "").strip().upper()

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                request_id,
                customer_name,
                service,
                problem,
                location,
                status,
                professional_id,
                professional_name
            FROM service_requests
            WHERE request_id = ?
            """,
            (request_id,)
        )

        request_data = cursor.fetchone()

        connection.close()

        if not request_data:
            error = "Request ID not found."

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Track Service Request - AkshNex</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 40px;
            }}

            .box {{
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}

            h1 {{
                text-align: center;
                color: #172033;
            }}

            input {{
                width: 100%;
                padding: 13px;
                margin-top: 10px;
                margin-bottom: 15px;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
            }}

            button {{
                width: 100%;
                padding: 13px;
                background: #172033;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                cursor: pointer;
            }}

            .result {{
                margin-top: 25px;
                padding: 20px;
                background: #f1f5f9;
                border-radius: 10px;
            }}

            .result p {{
                margin: 12px 0;
            }}

            .professional {{
                margin-top: 20px;
                padding: 15px;
                background: #eef0ff;
                border-radius: 10px;
            }}

            .professional h3 {{
                margin-top: 0;
                color: #5b5ce2;
            }}

            .error {{
                margin-top: 20px;
                color: red;
                text-align: center;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>Track Service Request</h1>

            <form method="POST">

                <label>Enter your Request ID</label>

                <input
                    type="text"
                    name="request_id"
                    placeholder="Example: AN-1001"
                    required
                >

                <button type="submit">
                    Track Request
                </button>

            </form>

            {"<div class='error'>" + error + "</div>" if error else ""}

            {
                f'''
                <div class="result">

                    <h3>Request Details</h3>

                    <p>
                        <strong>Request ID:</strong>
                        {request_data[0]}
                    </p>

                    <p>
                        <strong>Customer:</strong>
                        {request_data[1]}
                    </p>

                    <p>
                        <strong>Service:</strong>
                        {request_data[2]}
                    </p>

                    <p>
                        <strong>Problem:</strong>
                        {request_data[3]}
                    </p>

                    <p>
                        <strong>Location:</strong>
                        {request_data[4]}
                    </p>

                    <p>
                        <strong>Status:</strong>
                        {request_data[5]}
                    </p>

                    <div class="professional">

                        <h3>Assigned Professional</h3>

                        <p>
                            <strong>Name:</strong>
                            {request_data[7] if request_data[7] else "Not assigned yet"}
                        </p>

                        <p>
                            <strong>Professional ID:</strong>
                            {request_data[6] if request_data[6] else "Not assigned yet"}
                        </p>

                    </div>

                </div>
                '''
                if request_data else ""
            }

        </div>

    </body>

    </html>
    """

    
@app.route("/update-status", methods=["GET", "POST"])
def update_status():

    message = ""
    request_data = None

    if request.method == "POST":

        request_id = request.form.get("request_id", "").strip().upper()
        new_status = request.form.get("status")

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT request_id, customer_name, service, problem, location, status
            FROM service_requests
            WHERE request_id = ?
            """,
            (request_id,)
        )

        request_data = cursor.fetchone()

        if request_data:

            cursor.execute(
                """
                UPDATE service_requests
                SET status = ?
                WHERE request_id = ?
                """,
                (new_status, request_id)
            )

            connection.commit()

            message = "Status updated successfully!"

            cursor.execute(
                """
                SELECT request_id, customer_name, service, problem, location, status
                FROM service_requests
                WHERE request_id = ?
                """,
                (request_id,)
            )

            request_data = cursor.fetchone()

        else:
            message = "Request ID not found."

        connection.close()

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Update Service Status - AkshNex</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 40px;
            }}

            .box {{
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}

            h1 {{
                text-align: center;
                color: #172033;
            }}

            input, select {{
                width: 100%;
                padding: 13px;
                margin-top: 10px;
                margin-bottom: 15px;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
            }}

            button {{
                width: 100%;
                padding: 13px;
                background: #172033;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                cursor: pointer;
            }}

            .message {{
                margin-top: 20px;
                text-align: center;
                color: green;
                font-weight: bold;
            }}

            .result {{
                margin-top: 25px;
                padding: 20px;
                background: #f1f5f9;
                border-radius: 10px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>Update Service Status</h1>

            <form method="POST">

                <label>Request ID</label>

                <input
                    type="text"
                    name="request_id"
                    placeholder="Example: AN-1001"
                    required
                >

                <label>New Status</label>

                <select name="status" required>

                    <option value="Submitted">Submitted</option>
                    <option value="Accepted">Accepted</option>
                    <option value="Professional Assigned">Professional Assigned</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>

                </select>

                <button type="submit">
                    Update Status
                </button>

            </form>

            {"<div class='message'>" + message + "</div>" if message else ""}

            {
                f'''
                <div class="result">

                    <h3>Request Details</h3>

                    <p><strong>Request ID:</strong> {request_data[0]}</p>

                    <p><strong>Customer:</strong> {request_data[1]}</p>

                    <p><strong>Service:</strong> {request_data[2]}</p>

                    <p><strong>Problem:</strong> {request_data[3]}</p>

                    <p><strong>Location:</strong> {request_data[4]}</p>

                    <p><strong>Current Status:</strong> {request_data[5]}</p>

                </div>
                '''
                if request_data else ""
            }

        </div>

    </body>

    </html>
    """

@app.route("/professional-login", methods=["GET", "POST"])
def professional_login():

    message = ""

    if request.method == "POST":

        employee_id = request.form.get("employee_id", "").strip().upper()
        password = request.form.get("password", "")

        password_hash = hashlib.sha256(
            password.encode()
        ).hexdigest()

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT employee_id, employee_name, role
            FROM employees
            WHERE employee_id = ? AND password = ?
            """,
            (employee_id, password_hash)
        )

        employee = cursor.fetchone()

        connection.close()

        if employee:

            session["employee_id"] = employee[0]
            session["employee_name"] = employee[1]
            session["employee_role"] = employee[2]

            return """
            <script>
                window.location.href = "/professional-dashboard";
            </script>
            """

        else:

            message = "Invalid Employee ID or Password."

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Professional Login - AkshNex</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 40px;
            }}

            .login-box {{
                max-width: 420px;
                margin: 60px auto;
                background: white;
                padding: 35px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}

            h1 {{
                text-align: center;
                color: #172033;
                margin-bottom: 10px;
            }}

            .subtitle {{
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }}

            label {{
                display: block;
                margin-top: 15px;
                margin-bottom: 8px;
                font-weight: bold;
            }}

            input {{
                width: 100%;
                padding: 13px;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
            }}

            button {{
                width: 100%;
                padding: 13px;
                margin-top: 25px;
                background: #172033;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                cursor: pointer;
            }}

            button:hover {{
                opacity: 0.9;
            }}

            .error {{
                margin-top: 20px;
                padding: 12px;
                background: #fee2e2;
                color: #b91c1c;
                border-radius: 8px;
                text-align: center;
            }}

        </style>

    </head>

    <body>

        <div class="login-box">

            <h1>Professional Login</h1>

            <div class="subtitle">
                Login to access your AkshNex dashboard
            </div>

            <form method="POST">

                <label>Employee ID</label>

                <input
                    type="text"
                    name="employee_id"
                    placeholder="Example: EMP001"
                    required
                >

                <label>Password</label>

                <input
                    type="password"
                    name="password"
                    placeholder="Enter your password"
                    required
                >

                <button type="submit">
                    Login
                </button>

            </form>

            {"<div class='error'>" + message + "</div>" if message else ""}

        </div>

    </body>

    </html>
    """

@app.route("/professional-logout")
def professional_logout():

    session.clear()

    return """
    <script>
        window.location.href = "/professional-login";
    </script>
    """
@app.route("/professional-dashboard", methods=["GET", "POST"])
def professional_dashboard():
    if "employee_id" not in session:
        return """
        <script>
            window.location.href = "/professional-login";
        </script>
        """
    message = ""

    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    # Get available professionals
    cursor.execute(
        """
        SELECT employee_id, employee_name, role
        FROM employees
        ORDER BY employee_name
        """
    )

    professionals = cursor.fetchall()

    if request.method == "POST":

        request_id = request.form.get("request_id", "").strip().upper()
        action = request.form.get("action")

        # --------------------------------
        # ASSIGN PROFESSIONAL
        # --------------------------------

        if action == "assign":

            professional_id = request.form.get("professional_id")

            cursor.execute(
                """
                SELECT employee_id, employee_name
                FROM employees
                WHERE employee_id = ?
                """,
                (professional_id,)
            )

            professional = cursor.fetchone()

            if professional:

                professional_id = professional[0]
                professional_name = professional[1]

                cursor.execute(
                    """
                    UPDATE service_requests
                    SET professional_id = ?,
                        professional_name = ?,
                        status = ?
                    WHERE request_id = ?
                    """,
                    (
                        professional_id,
                        professional_name,
                        "Professional Assigned",
                        request_id
                    )
                )

                connection.commit()

                message = (
                    "Professional assigned successfully!"
                )

        # --------------------------------
        # UPDATE STATUS
        # --------------------------------

        elif action == "status":

            new_status = request.form.get("status")

            cursor.execute(
                """
                UPDATE service_requests
                SET status = ?
                WHERE request_id = ?
                """,
                (new_status, request_id)
            )

            connection.commit()

            message = (
                "Service request status updated successfully!"
            )

    # Get all service requests
    cursor.execute(
        """
        SELECT
            request_id,
            customer_name,
            service,
            problem,
            location,
            status,
            professional_id,
            professional_name
        FROM service_requests
        ORDER BY rowid DESC
        """
    )

    requests = cursor.fetchall()

    connection.close()

    rows_html = ""

    for item in requests:

        professional_options = ""

        for professional in professionals:

            selected = ""

            if item[6] == professional[0]:

                selected = "selected"

            professional_options += f"""
            <option value="{professional[0]}" {selected}>
                {professional[1]} ({professional[0]})
            </option>
            """

        assigned_professional = (
            item[7]
            if item[7]
            else "Not assigned"
        )

        rows_html += f"""
        <div class="request-card">

            <div class="request-top">

                <div>

                    <div class="request-id">
                        {item[0]}
                    </div>

                    <h2>
                        {item[2]}
                    </h2>

                </div>

                <div class="status">
                    {item[5]}
                </div>

            </div>

            <div class="details">

                <p>
                    <strong>Customer:</strong>
                    {item[1]}
                </p>

                <p>
                    <strong>Problem:</strong>
                    {item[3]}
                </p>

                <p>
                    <strong>Location:</strong>
                    {item[4]}
                </p>

                <p>
                    <strong>Assigned Professional:</strong>
                    {assigned_professional}
                </p>

            </div>

            <!-- ASSIGN PROFESSIONAL -->

            <form method="POST">

                <input
                    type="hidden"
                    name="request_id"
                    value="{item[0]}"
                >

                <input
                    type="hidden"
                    name="action"
                    value="assign"
                >

                <label>
                    Assign Professional
                </label>

                <select
                    name="professional_id"
                    required
                >

                    <option value="">
                        Select Professional
                    </option>

                    {professional_options}

                </select>

                <button type="submit">
                    Assign Professional
                </button>

            </form>

            <!-- UPDATE STATUS -->

            <form method="POST" class="status-form">

                <input
                    type="hidden"
                    name="request_id"
                    value="{item[0]}"
                >

                <input
                    type="hidden"
                    name="action"
                    value="status"
                >

                <label>
                    Update Status
                </label>

                <select
                    name="status"
                    required
                >

                    <option value="Submitted">
                        Submitted
                    </option>

                    <option value="Accepted">
                        Accepted
                    </option>

                    <option value="Professional Assigned">
                        Professional Assigned
                    </option>

                    <option value="In Progress">
                        In Progress
                    </option>

                    <option value="Completed">
                        Completed
                    </option>

                </select>

                <button type="submit">
                    Update Status
                </button>

            </form>

        </div>
        """

    if not rows_html:

        rows_html = """
        <div class="empty">
            No service requests found.
        </div>
        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Professional Dashboard - AkshNex</title>

        <style>

            * {{
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }}

            body {{
                margin: 0;
                background: #f5f7fb;
                color: #172033;
            }}

            header {{
                background: white;
                padding: 20px 7%;
                border-bottom: 1px solid #e5e7eb;
            }}

            .logo {{
                font-size: 28px;
                font-weight: 800;
            }}

            .logo span {{
                color: #5b5ce2;
            }}

            .container {{
                max-width: 1000px;
                margin: 35px auto;
                padding: 20px;
            }}

            .heading {{
                margin-bottom: 25px;
            }}

            .heading h1 {{
                margin-bottom: 8px;
            }}

            .heading p {{
                color: #697386;
            }}

            .message {{
                background: #e8f7ee;
                color: #16834b;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-weight: bold;
            }}

            .request-card {{
                background: white;
                padding: 25px;
                border-radius: 18px;
                margin-bottom: 20px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }}

            .request-top {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
            }}

            .request-id {{
                color: #5b5ce2;
                font-weight: bold;
                margin-bottom: 8px;
            }}

            .request-top h2 {{
                margin: 0;
            }}

            .status {{
                background: #eef0ff;
                color: #5b5ce2;
                padding: 8px 13px;
                border-radius: 20px;
                font-weight: bold;
            }}

            .details {{
                background: #f8fafc;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            }}

            .details p {{
                margin: 8px 0;
            }}

            label {{
                display: block;
                font-weight: bold;
                margin-bottom: 8px;
            }}

            select {{
                width: 100%;
                padding: 13px;
                border: 1px solid #d9deea;
                border-radius: 9px;
                font-size: 15px;
                margin-bottom: 12px;
            }}

            button {{
                width: 100%;
                padding: 13px;
                background: #172033;
                color: white;
                border: none;
                border-radius: 9px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
            }}

            button:hover {{
                opacity: 0.9;
            }}

            .status-form {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
            }}

            .empty {{
                background: white;
                padding: 30px;
                text-align: center;
                border-radius: 15px;
                color: #697386;
            }}

            .back {{
                display: block;
                text-align: center;
                margin-top: 25px;
                color: #5b5ce2;
                text-decoration: none;
            }}
            .logged-user {{
                text-align: center;
                margin-bottom: 25px;
                color: #555;
                font-size: 15px;
            }}

            .logged-user span {{
                color: #777;
            }}
        </style>

    </head>

    <body>

        <header>

            <div class="logo">
                Aksh<span>Nex</span>
            </div>

        </header>

        <div class="container">

            <div class="heading">

                <h1>
                    Professional Dashboard
                </h1>
                
                <div class="logged-user">

    <strong>Logged in as:</strong>
    {session.get("employee_name", "Professional")}

    <span>
        ({session.get("employee_role", "Professional")})
    </span>

</div>
<a href="/professional-logout">
    Logout
</a>
                <p>
                    View incoming service requests, assign professionals,
                    and manage service status.
                </p>

            </div>

            {"<div class='message'>" + message + "</div>" if message else ""}

            {rows_html}

            <a class="back" href="/">
                ← Back to AkshNex
            </a>

        </div>

    </body>

    </html>
    """
if __name__ == "__main__":
    app.run(debug=True)