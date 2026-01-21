# Science Knowledge Graph Data (Next Generation Science Standards - NGSS)
# Structure: Topics -> Core Ideas (Subtopics) -> Disciplinary Core Ideas (SubSubTopics) -> Concepts
# REFACTOR: SubSubTopics now split by Grade Band (Elementary, Middle, High) to segregate content.

topic_colors = {
    "Physical_Science": "100,200,255", 
    "Life_Science": "100,255,100",     
    "Earth_and_Space_Science": "200,150,100", 
    "Engineering_Technology": "150,150,150", 
    "Science_Library": "100,100,255",
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
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_Elementary",
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_Middle_School",
        "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_High_School",
        "Physical_Science->Matter_and_Its_Interactions->Chemical_Reactions_Elementary",
        "Physical_Science->Matter_and_Its_Interactions->Chemical_Reactions_Middle_School",
        "Physical_Science->Matter_and_Its_Interactions->Nuclear_Processes_High_School",
    ],
    "Physical_Science->Motion_and_Stability": [
        "Physical_Science->Motion_and_Stability->Forces_and_Motion_Elementary",
        "Physical_Science->Motion_and_Stability->Forces_and_Motion_Middle_School",
        "Physical_Science->Motion_and_Stability->Forces_and_Motion_High_School",
        "Physical_Science->Motion_and_Stability->Types_of_Interactions_Middle_School", # Example of only MS/HS
    ],
    "Physical_Science->Energy": [
        "Physical_Science->Energy->Definitions_of_Energy_Elementary",
        "Physical_Science->Energy->Definitions_of_Energy_Middle_School",
        "Physical_Science->Energy->Conservation_of_Energy_High_School",
        "Physical_Science->Energy->Energy_in_Chemical_Processes_High_School",
    ],
    "Physical_Science->Waves_and_Information": [
        "Physical_Science->Waves_and_Information->Wave_Properties_Elementary",
        "Physical_Science->Waves_and_Information->Wave_Properties_Middle_School",
        "Physical_Science->Waves_and_Information->Electromagnetic_Radiation_High_School",
    ],

    # Life Science
    "Life_Science->From_Molecules_to_Organisms": [
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_Elementary",
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_Middle_School",
        "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_High_School",
        "Life_Science->From_Molecules_to_Organisms->Growth_and_Development_Elementary",
        "Life_Science->From_Molecules_to_Organisms->Organization_for_Matter_and_Energy_Middle_School",
    ],
    "Life_Science->Ecosystems": [
        "Life_Science->Ecosystems->Interdependent_Relationships_Elementary",
        "Life_Science->Ecosystems->Interdependent_Relationships_Middle_School",
        "Life_Science->Ecosystems->Interdependent_Relationships_High_School",
        "Life_Science->Ecosystems->Cycles_of_Matter_Middle_School",
        "Life_Science->Ecosystems->Ecosystem_Dynamics_High_School",
    ],
    "Life_Science->Heredity": [
        "Life_Science->Heredity->Inheritance_of_Traits_Elementary",
        "Life_Science->Heredity->Inheritance_of_Traits_Middle_School",
        "Life_Science->Heredity->Variation_of_Traits_High_School",
    ],
    "Life_Science->Biological_Evolution": [
        "Life_Science->Biological_Evolution->Evidence_of_Common_Ancestry_Middle_School", # No elem usually
        "Life_Science->Biological_Evolution->Natural_Selection_Middle_School",
        "Life_Science->Biological_Evolution->Adaptation_Elementary",
        "Life_Science->Biological_Evolution->Adaptation_High_School",
    ],

    # Earth & Space
    "Earth_and_Space_Science->Earths_Place_in_the_Universe": [
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_Elementary",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_Middle_School",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_High_School",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->Earth_and_the_Solar_System_Middle_School",
        "Earth_and_Space_Science->Earths_Place_in_the_Universe->History_of_Planet_Earth_High_School",
    ],
    "Earth_and_Space_Science->Earths_Systems": [
        "Earth_and_Space_Science->Earths_Systems->Earth_Materials_and_Systems_Elementary",
        "Earth_and_Space_Science->Earths_Systems->Plate_Tectonics_Middle_School",
        "Earth_and_Space_Science->Earths_Systems->Weather_and_Climate_Elementary",
        "Earth_and_Space_Science->Earths_Systems->Weather_and_Climate_High_School",
    ],
    "Earth_and_Space_Science->Earth_and_Human_Activity": [
        "Earth_and_Space_Science->Earth_and_Human_Activity->Natural_Resources_Elementary",
        "Earth_and_Space_Science->Earth_and_Human_Activity->Natural_Hazards_Middle_School",
        "Earth_and_Space_Science->Earth_and_Human_Activity->Global_Climate_Change_High_School",
    ],

    # Engineering
    "Engineering_Technology->Engineering_Design": [
        "Engineering_Technology->Engineering_Design->Defining_Problems_Elementary",
        "Engineering_Technology->Engineering_Design->Defining_Problems_Middle_School",
        "Engineering_Technology->Engineering_Design->Defining_Problems_High_School",
        "Engineering_Technology->Engineering_Design->Developing_Solutions_Elementary",
        "Engineering_Technology->Engineering_Design->Optimizing_Solutions_Middle_School",
    ],

    # Library (No change needed, technically recommended, but we can band them too if user wants)
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
    "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_Elementary": [
        "Solids_Liquids_Gases_(Grade_2)", 
        "Particle_Model_(Grade_5)", 
    ],
    "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_Middle_School": [
        "Atoms_and_Molecules_(Grade_7)", 
    ],
    "Physical_Science->Matter_and_Its_Interactions->Structure_of_Matter_High_School": [
        "Atomic_Structure_(Grade_10)", 
    ],

    "Physical_Science->Motion_and_Stability->Forces_and_Motion_Elementary": [
        "Pushes_and_Pulls_(Grade_K)", 
        "Patterns_in_Motion_(Grade_3)", 
    ],
    "Physical_Science->Motion_and_Stability->Forces_and_Motion_Middle_School": [
        "Newtons_Laws_(Grade_8)", 
    ],
    "Physical_Science->Motion_and_Stability->Forces_and_Motion_High_School": [
        "Momentum_(Grade_11)", 
    ],
    
    # Life
    "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_Elementary": [
        "Animal_Needs_(Grade_K)", 
        "Animal_Body_Parts_(Grade_1)",
        "Plant_Structures_(Grade_4)", 
    ],
    "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_Middle_School": [
        "Cell_Theory_(Grade_6)", 
    ],
    "Life_Science->From_Molecules_to_Organisms->Structure_and_Function_High_School": [
        "DNA_and_Protein_Synthesis_(Grade_9)", 
    ],

    "Life_Science->Ecosystems->Interdependent_Relationships_Elementary": [
        "Food_Webs_(Grade_5)", 
    ],
    "Life_Science->Ecosystems->Interdependent_Relationships_Middle_School": [
        "Symbiosis_(Grade_7)", 
    ],
    "Life_Science->Ecosystems->Interdependent_Relationships_High_School": [
        "Carrying_Capacity_(Grade_9)", 
    ],

    # Earth
    "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_Elementary": [
        "Sun_and_Moon_(Grade_1)", 
        "Star_Brightness_(Grade_5)", 
    ],
    "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_Middle_School": [
        "Gravity_and_Orbits_(Grade_6)", 
    ],
    "Earth_and_Space_Science->Earths_Place_in_the_Universe->The_Universe_and_Its_Stars_High_School": [
        "Big_Bang_Theory_(Grade_12)", 
    ],

    # Engineering
    "Engineering_Technology->Engineering_Design->Defining_Problems_Elementary": [
        "Observing_World_(Grade_K)", 
        "Constraints_and_Criteria_(Grade_3)", 
    ],
    "Engineering_Technology->Engineering_Design->Defining_Problems_Middle_School": [
        "Precise_Design_Specs_(Grade_6)", 
    ],
    "Engineering_Technology->Engineering_Design->Defining_Problems_High_School": [
        "Global_Challenges_(Grade_10)", 
    ],

    # Fillers for the nodes I added in subsub_topics but didn't list in subsubsub (required for script not to crash?)
    # The script loops subsub_topics keys. If not in subsubsub, it's just an empty concepts list.
    # So I don't MUST define them, but good to have some placeholder if I want the key to exist with valid grade.
    # Note: If no concepts, the BubbleUp logic leaves it at default (99) or Topic default.
    # So I should probably add dummy concepts or map them if I care. 
    # For now, I only migrated the Core/Explicit ones from previous file. 
    # The others (e.g. Chemical_Reactions_Elementary) will be empty folders. 
    # This is fine for structure.
    
    # Library - keeping these together for now unless user asks to split library too.
    "Science_Library->Biographies->Famous_Physicists": [
        "Einstein_Life_(Grade_6-8)",
        "Marie_Curie_(Grade_6-8)",
        "Isaac_Newton_(Grade_9-12)",
    ],
    "Science_Library->Biographies->Naturalists": [
        "Jane_Goodall_(Grade_3-5)",
        "Darwin_Voyage_(Grade_9-12)", 
    ],
    "Science_Library->General_Science_Reading->Cosmos_Series": [
        "Carl_Sagan_Cosmos_(Grade_9-12)",
        "Neil_deGrasse_Tyson_Origins_(Grade_9-12)",
    ],
    "Science_Library->Science_Fiction_Hard": [
        "The_Martian_(Grade_9-12)",
        "Contact_(Grade_9-12)",
    ]
}
