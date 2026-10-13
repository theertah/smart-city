from fpdf import FPDF

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(37, 99, 235) # Blue
    pdf.cell(0, 15, "How the Smart City Platform Was Made", ln=True, align='C')
    pdf.ln(10)
    
    # Body
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    
    sections = [
        ("1. Architecture Overview", 
         "The AI Smart City Backend is built using a modern Python Flask framework for the backend "
         "API, combined with Vanilla JavaScript, HTML5, and CSS3 for the responsive dashboard. "
         "The database uses SQLite with SQLAlchemy as the ORM to store location data, traffic logs, "
         "complaints, and environmental metrics."),
         
        ("2. Backend & Blueprints", 
         "The backend is modularized into 'Blueprints' representing different domains: "
         "Traffic, Waste, Complaints, Predictions, and Environment. A background simulator "
         "job continuously generates simulated telemetry to mimic a live city environment."),
         
        ("3. AI & Predictions",
         "The platform integrates basic AI models to forecast traffic congestion and waste bin fill levels. "
         "An integrated AI assistant (using external APIs) can process natural language queries from citizens "
         "and return real-time city data."),
         
        ("4. Frontend Interface",
         "The frontend consists of an Admin Dashboard (index.html) and a Citizen Portal (citizen.html). "
         "We heavily utilized CSS variables to implement a dynamic Light/Dark mode. The map integration "
         "was built using Leaflet.js, mapping traffic zones and rendering congestion tooltips."),
         
        ("5. Development Workflow",
         "Development progressed from structuring the database schema, building out the REST APIs, "
         "implementing the background simulation, to styling the frontend dashboards. Bugs in the JavaScript "
         "Promises and null reference exceptions were resolved to create a stable, asynchronous frontend.")
    ]
    
    for title, text in sections:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(16, 185, 129) # Green
        pdf.cell(0, 10, title, ln=True)
        
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 8, text)
        pdf.ln(5)
        
    pdf.output("Smart_City_Documentation.pdf")

create_pdf()
