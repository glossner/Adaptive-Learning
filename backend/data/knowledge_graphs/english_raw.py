# English Knowledge Graph Data (Common Core State Standards + Exemplar Texts)
# Structure: Topics -> Subtopics -> SubSubTopics -> Concepts

topic_colors = {
    "Reading_Literature": "255,100,100",  # Red
    "Reading_Informational": "255,150,100", # Orange
    "Writing": "255,200,100", # Yellow-Orange
    "Language": "200,200,100", # Yellow
    "Speaking_and_Listening": "150,200,100", # Light Green
    "Literature_Library": "100,100,255", # Blue (Recommended)
}

# Mapping: Topic -> List of Subtopics (Arrow Notation)
topics_and_subtopics = {
    "Reading_Literature": [
        "Reading_Literature->Key_Ideas_and_Details",
        "Reading_Literature->Craft_and_Structure",
        "Reading_Literature->Integration_of_Knowledge",
    ],
    "Reading_Informational": [
        "Reading_Informational->Key_Ideas_and_Details",
        "Reading_Informational->Craft_and_Structure",
        "Reading_Informational->Integration_of_Knowledge",
    ],
    "Writing": [
        "Writing->Text_Types_and_Purposes",
        "Writing->Production_and_Distribution",
        "Writing->Research_to_Build_Knowledge",
    ],
    "Language": [
        "Language->Conventions_of_Standard_English",
        "Language->Knowledge_of_Language",
        "Language->Vocabulary_Acquisition",
    ],
    "Literature_Library": [
        "Literature_Library->Grade_K_1",
        "Literature_Library->Grade_2_3",
        "Literature_Library->Grade_4_5",
        "Literature_Library->Grade_6_8",
        "Literature_Library->Grade_9_10",
        "Literature_Library->Grade_11_12",
    ]
}

# Mapping: Subtopic -> List of SubSubTopics
subsub_topics = {
    # Reading Literature
    "Reading_Literature->Key_Ideas_and_Details": [
        "Reading_Literature->Key_Ideas_and_Details->Inference",
        "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary",
        "Reading_Literature->Key_Ideas_and_Details->Character_Development",
    ],
    "Reading_Literature->Craft_and_Structure": [
        "Reading_Literature->Craft_and_Structure->Word_Meaning",
        "Reading_Literature->Craft_and_Structure->Text_Structure",
        "Reading_Literature->Craft_and_Structure->Point_of_View",
    ],
    "Reading_Literature->Integration_of_Knowledge": [
        "Reading_Literature->Integration_of_Knowledge->Multimedia_Analysis",
        "Reading_Literature->Integration_of_Knowledge->Comparative_Literature",
    ],

    # Writing
    "Writing->Text_Types_and_Purposes": [
        "Writing->Text_Types_and_Purposes->Argumentative",
        "Writing->Text_Types_and_Purposes->Informative_Explanatory",
        "Writing->Text_Types_and_Purposes->Narrative",
    ],
    "Writing->Production_and_Distribution": [
        "Writing->Production_and_Distribution->Planning_and_Revising",
        "Writing->Production_and_Distribution->Technology_Use",
    ],
    
    # Language
    "Language->Conventions_of_Standard_English": [
        "Language->Conventions_of_Standard_English->Grammar_and_Usage",
        "Language->Conventions_of_Standard_English->Capitalization_and_Punctuation",
    ],
    "Language->Vocabulary_Acquisition": [
        "Language->Vocabulary_Acquisition->Context_Clues",
        "Language->Vocabulary_Acquisition->Figurative_Language",
    ],

    # Recommended Library (Electives/Exploration)
    "Literature_Library->Grade_K_1": [
        "Literature_Library->Grade_K_1->Picture_Books",
        "Literature_Library->Grade_K_1->Early_Readers",
    ],
    "Literature_Library->Grade_2_3": [
         "Literature_Library->Grade_2_3->Fables_and_Folktales",
         "Literature_Library->Grade_2_3->Beginner_Chapter_Books",
    ],
    "Literature_Library->Grade_4_5": [
        "Literature_Library->Grade_4_5->Myths_and_Legends",
        "Literature_Library->Grade_4_5->Classic_Childrens_Lit",
    ],
    "Literature_Library->Grade_6_8": [
        "Literature_Library->Grade_6_8->Young_Adult_Classics",
        "Literature_Library->Grade_6_8->Historical_Fiction",
        "Literature_Library->Grade_6_8->Plays_and_Poetry",
    ],
    "Literature_Library->Grade_9_10": [
        "Literature_Library->Grade_9_10->World_Literature",
        "Literature_Library->Grade_9_10->American_Literature_I",
        "Literature_Library->Grade_9_10->Shakespeare_Intro",
    ],
    "Literature_Library->Grade_11_12": [
        "Literature_Library->Grade_11_12->American_Literature_II",
        "Literature_Library->Grade_11_12->British_Literature",
        "Literature_Library->Grade_11_12->Complex_Texts",
    ]
}

# Mapping: SubSubTopic -> List of Concepts (Leaf Nodes)
# FORMAT: "Label" (Implicit Type=Core unless specified otherwise in conversion script)
subsubsub_topics = {
    # Reading
    "Reading_Literature->Key_Ideas_and_Details->Inference": [
        "Reading_Literature->Key_Ideas_and_Details->Inference->Ask_and_Answer_Questions", # K-2
        "Reading_Literature->Key_Ideas_and_Details->Inference->Refer_to_Text", # 3-5
        "Reading_Literature->Key_Ideas_and_Details->Inference->Cite_Textual_Evidence", # 6-8
        "Reading_Literature->Key_Ideas_and_Details->Inference->Strong_and_Thorough_Evidence", # 9-12
    ],
    "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary": [
         "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary->Retell_Stories",
         "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary->Determine_Theme",
         "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary->Objective_Summary",
         "Reading_Literature->Key_Ideas_and_Details->Theme_and_Summary->Complex_Theme_Analysis",
    ],
    
    # Writing
    "Writing->Text_Types_and_Purposes->Argumentative": [
        "Writing->Text_Types_and_Purposes->Argumentative->State_Opinion",
        "Writing->Text_Types_and_Purposes->Argumentative->Support_Claims",
        "Writing->Text_Types_and_Purposes->Argumentative->Counterarguments",
        "Writing->Text_Types_and_Purposes->Argumentative->Logical_Reasoning",
    ],

    # Language
    "Language->Conventions_of_Standard_English->Grammar_and_Usage": [
        "Language->Conventions_of_Standard_English->Grammar_and_Usage->Nouns_and_Verbs",
        "Language->Conventions_of_Standard_English->Grammar_and_Usage->Subject-Verb_Agreement",
        "Language->Conventions_of_Standard_English->Grammar_and_Usage->Pronoun-Antecedent_Agreement",
        "Language->Conventions_of_Standard_English->Grammar_and_Usage->Phrases_and_Clauses",
        "Language->Conventions_of_Standard_English->Grammar_and_Usage->Parallel_Structure",
    ],

    # LIBRARY (RECOMMENDED TEXTS)
    "Literature_Library->Grade_K_1->Picture_Books": [
        "Literature_Library->Grade_K_1->Picture_Books->The_Very_Hungry_Caterpillar",
        "Literature_Library->Grade_K_1->Picture_Books->Green_Eggs_and_Ham",
        "Literature_Library->Grade_K_1->Picture_Books->Where_the_Wild_Things_Are",
    ],
    "Literature_Library->Grade_2_3->Fables_and_Folktales": [
        "Literature_Library->Grade_2_3->Fables_and_Folktales->Aesops_Fables",
        "Literature_Library->Grade_2_3->Fables_and_Folktales->Cinderella_Variants",
    ],
    "Literature_Library->Grade_2_3->Beginner_Chapter_Books": [
        "Literature_Library->Grade_2_3->Beginner_Chapter_Books->Charlottes_Web",
        "Literature_Library->Grade_2_3->Beginner_Chapter_Books->Sarah_Plain_and_Tall",
    ],
    "Literature_Library->Grade_4_5->Classic_Childrens_Lit": [
        "Literature_Library->Grade_4_5->Classic_Childrens_Lit->Alice_in_Wonderland",
        "Literature_Library->Grade_4_5->Classic_Childrens_Lit->The_Secret_Garden",
        "Literature_Library->Grade_4_5->Classic_Childrens_Lit->Black_Beauty",
    ],
    "Literature_Library->Grade_6_8->Young_Adult_Classics": [
        "Literature_Library->Grade_6_8->Young_Adult_Classics->A_Wrinkle_in_Time",
        "Literature_Library->Grade_6_8->Young_Adult_Classics->The_Giver",
        "Literature_Library->Grade_6_8->Young_Adult_Classics->Roll_of_Thunder_Hear_My_Cry",
    ],
    "Literature_Library->Grade_6_8->Plays_and_Poetry": [
        "Literature_Library->Grade_6_8->Plays_and_Poetry->The_Road_Not_Taken",
        "Literature_Library->Grade_6_8->Plays_and_Poetry->Sorry_Wrong_Number",
    ],
    "Literature_Library->Grade_9_10->World_Literature": [
        "Literature_Library->Grade_9_10->World_Literature->The_Odyssey",
        "Literature_Library->Grade_9_10->World_Literature->Things_Fall_Apart",
    ],
    "Literature_Library->Grade_9_10->American_Literature_I": [
        "Literature_Library->Grade_9_10->American_Literature_I->To_Kill_a_Mockingbird",
        "Literature_Library->Grade_9_10->American_Literature_I->Of_Mice_and_Men",
        "Literature_Library->Grade_9_10->American_Literature_I->Fahrenheit_451",
    ],
    "Literature_Library->Grade_9_10->Shakespeare_Intro": [
        "Literature_Library->Grade_9_10->Shakespeare_Intro->Romeo_and_Juliet",
        "Literature_Library->Grade_9_10->Shakespeare_Intro->Julius_Caesar",
    ],
    "Literature_Library->Grade_11_12->American_Literature_II": [
        "Literature_Library->Grade_11_12->American_Literature_II->The_Great_Gatsby",
        "Literature_Library->Grade_11_12->American_Literature_II->The_Crucible",
        "Literature_Library->Grade_11_12->American_Literature_II->Their_Eyes_Were_Watching_God",
    ],
    "Literature_Library->Grade_11_12->British_Literature": [
        "Literature_Library->Grade_11_12->British_Literature->Macbeth",
        "Literature_Library->Grade_11_12->British_Literature->Hamlet",
        "Literature_Library->Grade_11_12->British_Literature->Pride_and_Prejudice",
        "Literature_Library->Grade_11_12->British_Literature->1984",
    ],
}
