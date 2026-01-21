# Science Knowledge Graph Data (Next Generation Science Standards - NGSS)
# Structure: Topics -> Core Ideas -> Disciplinary Core Ideas -> Concepts

topic_colors = {
    "Physical_Science": "100,200,255", # Cyany Blue
    "Life_Science": "100,255,100",     # Green
    "Earth_and_Space_Science": "200,150,100", # Brown/Terra
    "Engineering_Technology": "150,150,150", # Grey
    "Science_Library": "100,100,255", # Blue (Recommended)
}

topics_and_subtopics = {
    "Physical_Science": [
        "Physical_Science->Matter_and_Its_Interactions",
        "Physical_Science->Motion_and_Stability",
        "Physical_Science->Energy",
        "Physical_Science->Waves_and_Information",
    ],
    "Life_Science": [
        "Life_Science->From_Molecules_to_Organisms",
        "Life_Science->Ecosystems",
        "Life_Science->Heredity",
        "Life_Science->Biological_Evolution",
    ],
    "Earth_and_Space_Science": [
        "Earth_and_Space_Science->Earths_Place_in_the_Universe",
        "Earth_and_Space_Science->Earths_Systems",
        "Earth_and_Space_Science->Earth_and_Human_Activity",
    ],
    "Engineering_Technology": [
        "Engineering_Technology->Engineering_Design",
    ],
    "Science_Library": [
        "Science_Library->Biographies",
        "Science_Library->General_Science_Reading",
        "Science_Library->Science_Fiction_Hard",
    ]
}

subsub_topics = {
    # Physical Science
    "Physical_Science->Matter_and_Its_Interactions": [
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter",
        "Physical_Science->Matter_and_Its_Interactions->Chemical_Reactions",
        "Physical_Science->Matter_and_Its_Interactions->Nuclear_Processes",
    ],
    "Physical_Science->Motion_and_Stability": [
        "Physical_Science->Motion_and_Stability->Forces_and_Motion",
        "Physical_Science->Motion_and_Stability->Types_of_Interactions",
    ],
    "Physical_Science->Energy": [
        "Physical_Science->Energy->Definitions_of_Energy",
        "Physical_Science->Energy->Conservation_of_Energy",
        "Physical_Science->Energy->Energy_in_Chemical_Processes",
    ],
    "Physical_Science->Waves_and_Information": [
        "Physical_Science->Waves_and_Information->Wave_Properties",
        "Physical_Science->Waves_and_Information->Electromagnetic_Radiation",
    ],

    # Life Science
    "Life_Science->From_Molecules_to_Organisms": [
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function",
        "Life_Science->From_Molecules_to_Organisms->Growth_and_Development",
        "Life_Science->From_Molecules_to_Organisms->Organization_for_Matter_and_Energy",
    ],
    "Life_Science->Ecosystems": [
        "Life_Science->Ecosystems->Interdependent_Relationships",
        "Life_Science->Ecosystems->Cycles_of_Matter",
        "Life_Science->Ecosystems->Ecosystem_Dynamics",
    ],
    "Life_Science->Heredity": [
        "Life_Science->Heredity->Inheritance_of_Traits",
        "Life_Science->Heredity->Variation_of_Traits",
    ],
    "Life_Science->Biological_Evolution": [
        "Life_Science->Biological_Evolution->Evidence_of_Common_Ancestry",
        "Life_Science->Biological_Evolution->Natural_Selection",
        "Life_Science->Biological_Evolution->Adaptation",
    ],

    # Earth & Space
    "Earth_and_Space_Science->Earths_Place_in_the_Universe": [
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->Earth_and_the_Solar_System",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->History_of_Planet_Earth",
    ],
    "Earth_and_Space_Science->Earths_Systems": [
        "Earth_and_Space_Science->Earths_Systems->Earth_Materials_and_Systems",
        "Earth_and_Space_Science->Earths_Systems->Plate_Tectonics",
        "Earth_and_Space_Science->Earths_Systems->Weather_and_Climate",
    ],
    "Earth_and_Space_Science->Earth_and_Human_Activity": [
        "Earth_and_Space_Science->Earth_and_Human_Activity->Natural_Resources",
        "Earth_and_Space_Science->Earth_and_Human_Activity->Natural_Hazards",
        "Earth_and_Space_Science->Earth_and_Human_Activity->Global_Climate_Change",
    ],

    # Engineering
    "Engineering_Technology->Engineering_Design": [
        "Engineering_Technology->Engineering_Design->Defining_Problems",
        "Engineering_Technology->Engineering_Design->Developing_Solutions",
        "Engineering_Technology->Engineering_Design->Optimizing_Solutions",
    ],

    # Library
    "Science_Library->Biographies": [
        "Science_Library->Biographies->Famous_Physicists",
        "Science_Library->Biographies->Naturalists",
        "Science_Library->Biographies->Inventors",
    ],
    "Science_Library->General_Science_Reading": [
        "Science_Library->General_Science_Reading->Cosmos_Series",
        "Science_Library->General_Science_Reading->Nature_Writing",
    ],
    "Science_Library->Science_Fiction_Hard": [
        "Science_Library->Science_Fiction_Hard->Classic_SciFi",
        "Science_Library->Science_Fiction_Hard->Modern_SciFi",
    ]
}

subsubsub_topics = {
    # Physical
    "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter": [
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter->Solids_Liquids_Gases", # K-2
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter->Particle_Model", # 3-5
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter->Atoms_and_Molecules", # 6-8
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter->Atomic_Structure", # 9-12
    ],
    "Physical_Science->Motion_and_Stability->Forces_and_Motion": [
        "Physical_Science->Motion_and_Stability->Forces_and_Motion->Pushes_and_Pulls", # K-2
        "Physical_Science->Motion_and_Stability->Forces_and_Motion->Patterns_in_Motion", # 3-5
        "Physical_Science->Motion_and_Stability->Forces_and_Motion->Newtons_Laws", # 6-8
        "Physical_Science->Motion_and_Stability->Forces_and_Motion->Momentum", # 9-12
    ],
    
    # Life
    "Life_Science->From_Molecules_to_Organisms->Structure_and_Function": [
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function->Animal_Body_Parts", # K-2
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function->Plant_Structures", # 3-5
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function->Cell_Theory", # 6-8
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function->DNA_and_Protein_Synthesis", # 9-12
    ],
    "Life_Science->Ecosystems->Interdependent_Relationships": [
        "Life_Science->Ecosystems->Interdependent_Relationships->Animals_Need_Food", # K-2
        "Life_Science->Ecosystems->Interdependent_Relationships->Food_Webs", # 3-5
        "Life_Science->Ecosystems->Interdependent_Relationships->Symbiosis", # 6-8
        "Life_Science->Ecosystems->Interdependent_Relationships->Carrying_Capacity", # 9-12
    ],

    # Earth
    "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars": [
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars->Sun_Moon_Stars", # K-2
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars->Star_Brightness", # 3-5
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars->Gravity_and_Orbits", # 6-8
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars->Big_Bang_Theory", # 9-12
    ],

    # Engineering
    "Engineering_Technology->Engineering_Design->Defining_Problems": [
        "Engineering_Technology->Engineering_Design->Defining_Problems->Asking_Questions", # K-2
        "Engineering_Technology->Engineering_Design->Defining_Problems->Constraints_and_Criteria", # 3-5
        "Engineering_Technology->Engineering_Design->Defining_Problems->Precise_Design_Specs", # 6-8
        "Engineering_Technology->Engineering_Design->Defining_Problems->Global_Challenges", # 9-12
    ],

    # Library (Recommended)
    "Science_Library->Biographies->Famous_Physicists": [
        "Science_Library->Biographies->Famous_Physicists->Einstein_Life",
        "Science_Library->Biographies->Famous_Physicists->Marie_Curie",
        "Science_Library->Biographies->Famous_Physicists->Isaac_Newton",
    ],
    "Science_Library->Biographies->Naturalists": [
        "Science_Library->Biographies->Naturalists->Jane_Goodall",
        "Science_Library->Biographies->Naturalists->Darwin_Voyage",
    ],
    "Science_Library->General_Science_Reading->Cosmos_Series": [
        "Science_Library->General_Science_Reading->Cosmos_Series->Carl_Sagan_Cosmos",
        "Science_Library->General_Science_Reading->Cosmos_Series->Neil_deGrasse_Tyson_Origins",
    ],
    "Science_Library->Science_Fiction_Hard": [
        "Science_Library->Science_Fiction_Hard->Classic_SciFi->The_Martian",
        "Science_Library->Science_Fiction_Hard->Classic_SciFi->Contact",
    ],
}
