# Social Studies Knowledge Graph Data (C3 Framework)
# Structure: Topics -> Subtopics -> SubSubTopics -> Concepts

topic_colors = {
    "History": "200,100,100", # Red/Brown
    "Geography": "100,200,100", # Green
    "Civics_and_Government": "100,100,200", # Blue
    "Economics": "200,200,100", # Gold
    "Historical_Library": "150,100,255", # Purple (Recommended)
}

topics_and_subtopics = {
    "History": [
        "History->Change_Continuity_and_Context",
        "History->Perspectives",
        "History->Historical_Sources_and_Evidence",
        "History->Causation_and_Argumentation",
    ],
    "Geography": [
        "Geography->Geographic_Representations",
        "Geography->Human_Environment_Interaction",
        "Geography->Human_Population",
        "Geography->Global_Interconnections",
    ],
    "Civics_and_Government": [
        "Civics_and_Government->Civic_and_Political_Institutions",
        "Civics_and_Government->Participation_and_Deliberation",
        "Civics_and_Government->Processes_Rules_and_Laws",
    ],
    "Economics": [
        "Economics->Economic_Decision_Making",
        "Economics->Exchange_and_Markets",
        "Economics->National_Economy",
        "Economics->Global_Economy",
    ],
    "Historical_Library": [
        "Historical_Library->Biographies",
        "Historical_Library->Primary_Sources",
        "Historical_Library->Historical_Fiction",
    ]
}

subsub_topics = {
    # History
    "History->Change_Continuity_and_Context": [
        "History->Change_Continuity_and_Context->Chronology",
        "History->Change_Continuity_and_Context->Historical_Context",
    ],
    "History->Perspectives": [
        "History->Perspectives->Understanding_Perspectives",
        "History->Perspectives->Historical_Influence",
    ],
    "History->Historical_Sources_and_Evidence": [
        "History->Historical_Sources_and_Evidence->Gathering_Evidence",
        "History->Historical_Sources_and_Evidence->Critiquing_Sources",
    ],
    "History->Causation_and_Argumentation": [
        "History->Causation_and_Argumentation->Cause_and_Effect",
        "History->Causation_and_Argumentation->Claims_and_Counterclaims",
    ],

    # Geography
    "Geography->Geographic_Representations": [
        "Geography->Geographic_Representations->Maps_and_Globes",
        "Geography->Geographic_Representations->Geospatial_Technologies",
    ],
    "Geography->Human_Environment_Interaction": [
        "Geography->Human_Environment_Interaction->Cultural_Diffusion",
        "Geography->Human_Environment_Interaction->Resource_Distribution",
    ],

    # Civics
    "Civics_and_Government->Civic_and_Political_Institutions": [
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government",
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government",
        "Civics_and_Government->Civic_and_Political_Institutions->Constitutional_Principles",
    ],
    "Civics_and_Government->Processes_Rules_and_Laws": [
        "Civics_and_Government->Processes_Rules_and_Laws->Rule_of_Law",
        "Civics_and_Government->Processes_Rules_and_Laws->Law_Making_Process",
    ],

    # Economics
    "Economics->Economic_Decision_Making": [
        "Economics->Economic_Decision_Making->Scarcity_and_Choice",
        "Economics->Economic_Decision_Making->Incentives",
    ],
    "Economics->Exchange_and_Markets": [
        "Economics->Exchange_and_Markets->Supply_and_Demand",
        "Economics->Exchange_and_Markets->Trade_and_Money",
    ],

    # Library
    "Historical_Library->Biographies": [
        "Historical_Library->Biographies->Founding_Fathers",
        "Historical_Library->Biographies->Civil_Rights_Leaders",
        "Historical_Library->Biographies->World_Leaders",
    ],
    "Historical_Library->Primary_Sources": [
        "Historical_Library->Primary_Sources->US_Founding_Documents",
        "Historical_Library->Primary_Sources->Speeches",
    ],
    "Historical_Library->Historical_Fiction": [
        "Historical_Library->Historical_Fiction->World_War_II",
        "Historical_Library->Historical_Fiction->Colonial_Era",
    ]
}

subsubsub_topics = {
    # History
    "History->Change_Continuity_and_Context->Chronology": [
        "History->Change_Continuity_and_Context->Chronology->Timelines", # K-2
        "History->Change_Continuity_and_Context->Chronology->Eras_and_Periods", # 3-5
        "History->Change_Continuity_and_Context->Chronology->Complex_Causality", # 6-8
        "History->Change_Continuity_and_Context->Chronology->Historiography", # 9-12
    ],

    # Geography
    "Geography->Geographic_Representations->Maps_and_Globes": [
        "Geography->Geographic_Representations->Maps_and_Globes->Map_Symbols", # K-2
        "Geography->Geographic_Representations->Maps_and_Globes->Coordinates_and_Scale", # 3-5
        "Geography->Geographic_Representations->Maps_and_Globes->Thematic_Maps", # 6-8
        "Geography->Geographic_Representations->Maps_and_Globes->GIS_Analysis", # 9-12
    ],

    # Civics
    "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government": [
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government->Community_Helpers", # K-2
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government->Local_vs_State", # 3-5
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government->Preamble_Goals", # 6-8
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government->Political_Philosophy", # 9-12
    ],
    "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government": [
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government->Leaders", # K-2
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government->Separation_of_Powers", # 3-5
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government->Checks_and_Balances", # 6-8
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government->Federalism", # 9-12
    ],

    # Economics
    "Economics->Economic_Decision_Making->Scarcity_and_Choice": [
        "Economics->Economic_Decision_Making->Scarcity_and_Choice->Wants_vs_Needs", # K-2
        "Economics->Economic_Decision_Making->Scarcity_and_Choice->Opportunity_Cost", # 3-5
        "Economics->Economic_Decision_Making->Scarcity_and_Choice->Cost_Benefit_Analysis", # 6-8
        "Economics->Economic_Decision_Making->Scarcity_and_Choice->Marginal_Analysis", # 9-12
    ],

    # Library (Recommended)
    "Historical_Library->Biographies->Founding_Fathers": [
        "Historical_Library->Biographies->Founding_Fathers->George_Washington",
        "Historical_Library->Biographies->Founding_Fathers->Benjamin_Franklin",
        "Historical_Library->Biographies->Founding_Fathers->Alexander_Hamilton",
    ],
    "Historical_Library->Biographies->Civil_Rights_Leaders": [
        "Historical_Library->Biographies->Civil_Rights_Leaders->MLK_Jr",
        "Historical_Library->Biographies->Civil_Rights_Leaders->Rosa_Parks",
        "Historical_Library->Biographies->Civil_Rights_Leaders->Malcolm_X",
    ],
    "Historical_Library->Primary_Sources->US_Founding_Documents": [
        "Historical_Library->Primary_Sources->US_Founding_Documents->Declaration_of_Independence",
        "Historical_Library->Primary_Sources->US_Founding_Documents->The_Constitution",
        "Historical_Library->Primary_Sources->US_Founding_Documents->Bill_of_Rights",
    ],
    "Historical_Library->Historical_Fiction->World_War_II": [
        "Historical_Library->Historical_Fiction->World_War_II->Number_the_Stars",
        "Historical_Library->Historical_Fiction->World_War_II->Diary_of_Anne_Frank",
    ],
}
