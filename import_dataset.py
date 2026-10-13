import os
import csv
import glob
from datetime import datetime, timedelta
from app import create_app
from database.db import db
from database.models import Location, Waste

def import_waste_data():
    app = create_app()
    with app.app_context():
        print("Starting dataset import...")
        base_dir = os.path.join("dataset", "extracted", "Deliver_data")
        
        info_file = os.path.join(base_dir, "INFO.csv")
        if not os.path.exists(info_file):
            print(f"Error: Could not find {info_file}")
            return
            
        print("Reading container info...")
        container_locations = {}
        with open(info_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                container_id = int(float(row["ID"]))
                # Create or get Location
                loc = Location.query.filter_by(name=f"Bin {container_id}").first()
                if not loc:
                    loc = Location(
                        name=f"Bin {container_id}",
                        zone=row["WasteType"],
                        latitude=float(row["Latitude"]),
                        longitude=float(row["Longitude"])
                    )
                    db.session.add(loc)
                    db.session.commit()
                container_locations[container_id] = loc.location_id
                
        print(f"Loaded {len(container_locations)} container locations.")
        
        print("Importing waste fill levels (this may take a minute)...")
        fill_files = glob.glob(os.path.join(base_dir, "*_fill_Corrected_with_metrics.csv"))
        
        # We will shift all timestamps forward so the dashboard looks "Live" today.
        # Find the max date in the dataset first to know the offset.
        max_date_in_dataset = datetime(2000, 1, 1)
        # For speed, we won't scan all files for max date, let's assume it ends around Dec 2021.
        # We'll just shift everything by adding roughly 3 years (1095 days).
        time_shift = timedelta(days=1200)
        
        total_records = 0
        for file in fill_files:
            filename = os.path.basename(file)
            # Example: Container_1000_fill_Corrected_with_metrics.csv
            container_id_str = filename.split("_")[1]
            try:
                container_id = int(container_id_str)
            except ValueError:
                continue
                
            location_id = container_locations.get(container_id)
            if not location_id:
                continue
                
            with open(file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = []
                for row in reader:
                    if not row.get("Fill"):
                        continue
                        
                    raw_date = row["Date"]
                    try:
                        dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                        dt = dt + time_shift # Shift to current timeline
                    except ValueError:
                        continue
                        
                    fill_pct = float(row["Fill"])
                    records.append(Waste(
                        location_id=location_id,
                        timestamp=dt,
                        fill_percentage=fill_pct
                    ))
                    total_records += 1
                
                if records:
                    db.session.bulk_save_objects(records)
                    db.session.commit()
                    
        print(f"Successfully imported {total_records} real waste data records into the database!")

if __name__ == "__main__":
    import_waste_data()
