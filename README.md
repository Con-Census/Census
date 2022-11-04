# Con-census: Climate Risk Assessment 

## Project Summary
- The initial data indicated that the New York and California have highest risk in the United States and studies found to back the findings.
- The South region has most diversed cost versus pop_density
The South region has as the author Cindy Ermus wrote in her book,"The Gulf South, and the Gulf Coast in particular, is bound together by much more than geography or the shared experience of risk and vulnerability to wind, water, erosion, and biological exchanges,” she writes. “More fundamentally, the environment has helped define the region’s identity and largely determined its history, its social fabric, and its economy.” We can assumed, based on this graph that south region has significant high risk compare to other regions.

***
[[Goal](#goal)]
[[Project Descriptions](#project-descriptions)]
[[Deliverables](#deliverables)]
[[Data Dictionary](#data-dictionary)]
[[Initial Hypotheses](#initial-hypotheses)]
[[Exeucitve Summary](#executive-summary)]
[[Planning](#planning)]
[[Recommendation, Conclusion, and Next Step](#recommendation,-conclusion,-and-next-step)]
[[Steps to Reproduce](#steps-to-reproduce)]
___

## Goal
- This project aims to create a Machine Learning model to predict which State in the U.S. has most support from the government.

***
## Project Descriptions
- Climate Change and Global Warming refer to the long term shift in termperature and weather. Which impacts the Earth's climate system. 'Due to climate change, deserts are expanding, while heat waves and wildfires are becoming more common. Increased warming in the Arctic has contributed to melting permafrost, glacial retreat and sea ice loss. Higher temperatures are also causing more intense storms, droughts, and other weather extremes.' [Wikipedia](https://en.wikipedia.org/wiki/Climate_change).
- 'Sixty percent of Fortune 500 companies have set goals to act on the climate crisis and address energy use,'[worldwildlife.org](https://www.worldwildlife.org/stories/fortune-500-companies-are-acting-on-the-climate-crisis-but-is-it-enough). This project will hope to create a supporting level that a region received to help Fortune 500 companies to identify potential business risk. The project would also assist people to decide which community would be idea to move into.

***
## Deliverables
- 

***
## Data Dictionary

|Target|Definition
|:-------|:----------|
|support_value|Funds available minus total cost of damages|

|Feature|Definition|
|:-------|:----------|
|full_state  |State Full Name|
|state   |State Acronym|
|county  |County Name|
|population    |Population|
|revenue_per_person  |Tax revenue per person|
|state_funding  |Total tax revenue|
|fed_funding  |Funding awarded by federal government|
|buildvalue      |Building Value ($)|
|agrivalue       |Agriculture Value ($)| 
|area   |Area (sq mi)|
|risk_score       |National Risk Index - Score - Composite|
|resl_score  |Community Resilience - Score|
|resl_value  |Community Resilience - Value|
|drought_freq  |Annualized frequency of droughts|
|drought_score  |Drought - Hazard Type Risk Index Score|
|drought_loss  |Drought - Total Amount of Damages per event ($)|
|hurricane_freq  |Annualized frequency of hurricanes|
|hurricane_score  |Hurricane - Hazard Type Risk Index Score|
|hurricane_loss  |Hurricane - Total Amount of Damages per event ($)|
|storm_freq |Annualized frequency of severe storms|
|storm_score  |Severe Storm - Hazard Type Risk Index Score|
|storm_loss  |Severe Storm - Total Amount of Damages per event($)|
|pop_density  |the density of the population calculated from population/area|
|cost  |the total cost of three disaster|
|support value  |how much the funding left after support the total cost|
|support level  |what is the level of the support that the government rendered|

***
## Panning
- We create README.md file
- Create wrangle.py file
    - wrangle.py will clean the datasets from various website
    - the wrangle will set a strong foundation for our exploration and modeling
- Create explore.py file
    - we will ask some intial questions, and assumptions during this phase
    - we will further expand our questions scope as we discover information from our dataset
- we will create the classification model to support our discover

***
## Initial Questions
- Whether the dense of the populatop matter
- The cost of the disaster per region
- The south region has higher risk than any other regions

***
# Recommendation, Conclusion, and Next Step

## Recommendation
- The 
- The RandomForestClassifer can be used for our prediction

## Conclusion 
- The initial data indicated that the New York and California have highest risk in the United States and studies found to back the findings.
- The South region has most diversed cost versus pop_density
The South region has as the author Cindy Ermus wrote in her book,"The Gulf South, and the Gulf Coast in particular, is bound together by much more than geography or the shared experience of risk and vulnerability to wind, water, erosion, and biological exchanges,” she writes. “More fundamentally, the environment has helped define the region’s identity and largely determined its history, its social fabric, and its economy.” We can assumed, based on this graph that south region has significant high risk compare to other regions

## Next Step
- Expand the scope of the data
- Improvise the machine learning model
- Would do a seperate studies regarding New York and California

***
## Steps to Reproduce
- Download the folder and all files from the repo
- install tabula and plotly libary
- Enjoy!
***