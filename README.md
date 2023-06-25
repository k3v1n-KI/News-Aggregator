# News-Aggregator
This is a news aggregator that detects media bias and fake news with each article it aggregates. 
It correlates news using a news API that returns the articles and their corresponding metadata in a JSON format. As the news articles are gotten, they are passed through two machine learning models.  
One of the models is a media bias detection model and it is gotten from python's "Textblob" library. This model was used to detect the subjectivity of articles on a scale of zero to one (zero being the least subjective and one being the most subjective).
The second model is a Reccurent Neural Network that predicts the authenticaticity of the articles gotten from the news API. The dataset used had labels that were binary in nature so prediction can either be zero or one (zero being fake, and one being authentic).  
