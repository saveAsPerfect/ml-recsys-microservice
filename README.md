# ML Recommender Microservice

![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![CatBoost](https://img.shields.io/badge/CatBoost-Ranker-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)

## Project Overview
This microservice provides personalized post recommendations using FastAPI and CatBoost.
The service generates recommendations for a user based on their like history, precomputed user and post features, and temporal context.

## Metrics
Model performance is assessed primarily using HitRate@5, defined as:

<br>
<p align="center">
  <img src="https://latex.codecogs.com/svg.image?\large&space;\color{White}Hitrate@5=\frac{1}{n\cdot&space;T}\sum_{t=1}^{T}\sum_{i=1}^{n}\min\left(1,\sum_{j=1}^{5}\left[a_j(x_i,&space;t)=1\right]\right)" alt="Hitrate formula">
</p>


where:  
- n – number of users  
- T – number of test periods  
- a(x,t) – indicator function: whether the \(j\)-th recommended post for user \(i\) at time \(t\) was actually liked.


### Additional Metrics:

- **NDCG@K (Normalized Discounted Cumulative Gain)** – evaluates ranking quality by considering the positions of relevant items.
- **Recall@K (per-user)** – average fraction of a user's liked posts captured in the top-K recommendations.
- **Precision@K** – fraction of recommended posts that were actually liked.
- **YetiRank loss** – CatBoost’s pairwise ranking loss, used as the training objective to optimize ranking order.




## Architecture

1. **Candidate Generation** – retrieves ~200 candidate posts using pre-trained models (SVD or top-popular posts).  
2. **Ranking** – CatBoost Ranker scores candidates with user, post, and time-based features; BERT embeddings enrich post text features.  
3. **A/B Testing** – users are split into control and test groups, each served by a separate model.

## API Endpoint
  Swagger UI http://localhost:8000/docs

```GET /post/recommendations/```

Query parameters:

- user_id: int – user identifier.
- time: datetime – current timestamp (used for temporal features).
- limit: int – number of recommendations to return (default: 5).


```json
{
  "exp_group": "control",
  "recommendations": [
    {"id": 1141, "text": "Post content...", "topic": "sport"},
    {"id": 1634, "text": "Post content...", "topic": "tech"}
  ]
}
```


## 📋 Example Usage

### Curl:
```bash
curl "http://localhost:8000/api/v1/post/recommendations/?user_id=123&time=2024-01-15T10:30:00&limit=5"
```

### Requests:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/post/recommendations/",
    params={
        "user_id": 123,
        "time": "2024-01-15T10:30:00",
        "limit": 5
    }
)
recommendations = response.json()
```

## 🔧 Configuration

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `MODEL_CONTROL_PATH` - Path to control model
- `MODEL_TEST_PATH` - Path to test model
- `USER_FEATURES_QUERY` - SQL query for user features
- `POST_FEATURES_QUERY` - SQL query for post features
