import pandas as pd
import numpy as np
from catboost import Pool
from catboost import CatBoostRanker


post_data = pd.read_csv('post_data.csv')
user_data = pd.read_csv('user_data.csv')

# Load Data (with correct features)
train = pd.read_csv('train_balanced.csv')
test=pd.read_csv('test_balanced.csv')

train = train.merge(post_data,on='post_id',how='left')
train = train.merge(user_data,on='user_id',how='left')

test = test.merge(post_data,on='post_id',how='left')
test = test.merge(user_data,on='user_id',how='left')


# select features 
features = ['gender','age','topic','country','city','os','rating']
cat_features = ['topic','city','os','country']

# creat data pool for catboost
train_pool = Pool(
    data=train[features],
    label=train['target'],
    group_id=train['user_id'],
    cat_features=cat_features
)

test_pool = Pool(
    data=test[features],
    label=test['target'],
    group_id=test['user_id'],
    cat_features=cat_features
)


# train
rank_model = CatBoostRanker(
    iterations=500,
    loss_function='YetiRank',
    eval_metric='NDCG:top=10',
    custom_metric=[
        'PrecisionAt:top=5',
        'RecallAt:top=5',
        'MAP:top=5'
    ],
    verbose=100,
    thread_count=10
)

rank_model.fit(train_pool, eval_set=test_pool, use_best_model=True)

# final train 
best_params = rank_model.get_params()


full_data = pd.concat([train, test], axis=0)

X_full = full_data[features]
y_full = full_data['target']
group_full = full_data['user_id']  

full_pool = Pool(
    data=X_full,
    label=y_full,
    group_id=group_full,
    cat_features=cat_features
)

final_model = CatBoostRanker(**best_params)
final_model.fit(full_pool)

final_model.save_model('final_model',format='cbm')