# Social Studies Knowledge Graph Data (C3 Framework)
# Structure: Topics -> Subtopics -> SubSubTopics -> Concepts
# REFACTOR: Split SubSubTopics by Grade Band (Elementary, Middle, High)

topic_colors = {
    "History": "200,100,100", 
    "Geography": "100,200,100", 
    "Civics_and_Government": "100,100,200", 
    "Economics": "200,200,100", 
    "Historical_Library": "150,100,255", 
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
        "History->Change_Continuity_and_Context->Chronology_Elementary",
        "History->Change_Continuity_and_Context->Chronology_Middle_School",
        "History->Change_Continuity_and_Context->Chronology_High_School",
        "History->Change_Continuity_and_Context->Historical_Context_Elementary",
    ],
    "History->Perspectives": [
        "History->Perspectives->Understanding_Perspectives_Elementary",
        "History->Perspectives->Historical_Influence_Middle_School",
    ],
    "History->Historical_Sources_and_Evidence": [
        "History->Historical_Sources_and_Evidence->Gathering_Evidence_Elementary",
        "History->Historical_Sources_and_Evidence->Critiquing_Sources_High_School",
    ],
    "History->Causation_and_Argumentation": [
        "History->Causation_and_Argumentation->Cause_and_Effect_Elementary",
        "History->Causation_and_Argumentation->Claims_and_Counterclaims_Middle_School",
    ],

    # Geography
    "Geography->Geographic_Representations": [
        "Geography->Geographic_Representations->Maps_and_Globes_Elementary",
        "Geography->Geographic_Representations->Maps_and_Globes_Middle_School",
        "Geography->Geographic_Representations->Maps_and_Globes_High_School",
        "Geography->Geographic_Representations->Geospatial_Technologies_High_School",
    ],
    "Geography->Human_Environment_Interaction": [
        "Geography->Human_Environment_Interaction->Cultural_Diffusion_Middle_School",
        "Geography->Human_Environment_Interaction->Resource_Distribution_Elementary",
    ],

    # Civics
    "Civics_and_Government->Civic_and_Political_Institutions": [
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_Elementary",
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_Middle_School",
        "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_High_School",
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_Elementary",
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_Middle_School",
        "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_High_School",
        "Civics_and_Government->Civic_and_Political_Institutions->Constitutional_Principles_Middle_School",
    ],
    "Civics_and_Government->Processes_Rules_and_Laws": [
        "Civics_and_Government->Processes_Rules_and_Laws->Rule_of_Law_Elementary",
        "Civics_and_Government->Processes_Rules_and_Laws->Law_Making_Process_Middle_School",
    ],

    # Economics
    "Economics->Economic_Decision_Making": [
        "Economics->Economic_Decision_Making->Scarcity_and_Choice_Elementary",
        "Economics->Economic_Decision_Making->Scarcity_and_Choice_Middle_School",
        "Economics->Economic_Decision_Making->Scarcity_and_Choice_High_School",
        "Economics->Economic_Decision_Making->Incentives_Elementary",
    ],
    "Economics->Exchange_and_Markets": [
        "Economics->Exchange_and_Markets->Supply_and_Demand_Middle_School",
        "Economics->Exchange_and_Markets->Trade_and_Money_Elementary",
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
    "History->Change_Continuity_and_Context->Chronology_Elementary": [
        "Sequencing_Events_(Grade_K)", 
        "Timelines_(Grade_1)",
        "Eras_and_Periods_(Grade_3)", 
    ],
    "History->Change_Continuity_and_Context->Chronology_Middle_School": [
        "Complex_Causality_(Grade_6)", 
    ],
    "History->Change_Continuity_and_Context->Chronology_High_School": [
        "Historiography_(Grade_9)", 
    ],

    # Geography
    "Geography->Geographic_Representations->Maps_and_Globes_Elementary": [
        "Map_Symbols_(Grade_2)", 
        "Coordinates_and_Scale_(Grade_4)", 
    ],
    "Geography->Geographic_Representations->Maps_and_Globes_Middle_School": [
        "Thematic_Maps_(Grade_7)", 
    ],
    "Geography->Geographic_Representations->Maps_and_Globes_High_School": [
        "GIS_Analysis_(Grade_12)", 
    ],

    # Civics
    "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_Elementary": [
        "Community_Helpers_(Grade_K)", 
        "Local_vs_State_Gov_(Grade_3)", 
    ],
    "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_Middle_School": [
        "Preamble_Goals_(Grade_8)", 
    ],
    "Civics_and_Government->Civic_and_Political_Institutions->Role_of_Government_High_School": [
        "Political_Philosophy_(Grade_10)", 
    ],

    "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_Elementary": [
        "Leaders_(Grade_1)", 
        "Separation_of_Powers_(Grade_4)", 
    ],
    "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_Middle_School": [
        "Checks_and_Balances_(Grade_8)", 
    ],
    "Civics_and_Government->Civic_and_Political_Institutions->Branches_of_Government_High_School": [
        "Federalism_(Grade_11)", 
    ],

    # Economics
    "Economics->Economic_Decision_Making->Scarcity_and_Choice_Elementary": [
        "Wants_vs_Needs_(Grade_1)", 
        "Opportunity_Cost_(Grade_5)", 
    ],
    "Economics->Economic_Decision_Making->Scarcity_and_Choice_Middle_School": [
        "Cost_Benefit_Analysis_(Grade_6)", 
    ],
    "Economics->Economic_Decision_Making->Scarcity_and_Choice_High_School": [
        "Marginal_Analysis_(Grade_12)", 
    ],

    # Library (Recommended)
    "Historical_Library->Biographies->Founding_Fathers": [
        "George_Washington_(Grade_3)",
        "Benjamin_Franklin_(Grade_5)",
        "Alexander_Hamilton_(Grade_11)",
    ],
    "Historical_Library->Biographies->Civil_Rights_Leaders": [
        "Rosa_Parks_(Grade_K)",
        "MLK_Jr_(Grade_3)",
        "Malcolm_X_(Grade_11)",
    ],
    "Historical_Library->Primary_Sources->US_Founding_Documents": [
        "Declaration_of_Independence_(Grade_8)",
        "The_Constitution_(Grade_11)",
        "Bill_of_Rights_(Grade_11)",
    ],
    "Historical_Library->Historical_Fiction->World_War_II": [
        "Number_the_Stars_(Grade_6)",
        "Diary_of_Anne_Frank_(Grade_8)",
    ],
}
