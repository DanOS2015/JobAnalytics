import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestClassifier
from .models import UserApplication
from django.contrib.staticfiles.storage import staticfiles_storage


def classification_model():
    dataset = pd.read_csv('frontend/static/frontend/datasets/HR_comma_sep.csv')
    del dataset['sales']
    dataset = pd.get_dummies(dataset, columns=['salary'])
    dataset = shuffle(dataset)

    dataset.loc[(dataset['last_evaluation'] >= 0.695), 'work_ethic'] = "Excellent Worker"
    dataset.loc[((dataset['last_evaluation'] < 0.695) & (dataset['last_evaluation'] >= 0.395)), 'work_ethic'] = "Satisfactory Worker"
    dataset.loc[(dataset['last_evaluation'] < 0.395), 'work_ethic'] = "Poor Worker"

    del dataset['last_evaluation']

    x = dataset.drop('work_ethic', axis=1)
    y = dataset['work_ethic']

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)

    random_forest = RandomForestClassifier(criterion='entropy')
    random_forest.fit(X_train, y_train)

    return random_forest


def predict_performance(application):
    '''
    input structure for prediction: satisfaction_level, number_project, average_monthly_hours,
    time_spend_at_company, work_accident, left, promotion_last_5_years, salary_high, salary_med, salary_low
    '''

    model = classification_model()

    satisfaction = (application.satisfaction_level/100)
    number_project = application.number_of_projects
    monthly_hours = application.average_monthly_hours
    time_spent_at_company = application.time_spent_at_company

    if application.work_accident == '1':
        work_accident = 1
    else:
        work_accident = 0

    left = 1

    if application.promotion_in_last_5_years == '1':
        promotion_last_5_years = 1
    else:
        promotion_last_5_years = 0

    if application.average_salary == 'low':
        salary_low = 1
        salary_med = 0
        salary_high = 0
    elif application.average_salary == 'med':
        salary_low = 0
        salary_med = 1
        salary_high = 0
    else:
        salary_low = 0
        salary_med = 0
        salary_high = 1

    return model.predict([[
        satisfaction,
        number_project,
        monthly_hours,
        time_spent_at_company,
        work_accident,
        left,
        promotion_last_5_years,
        salary_high,
        salary_med,
        salary_low
    ]])
