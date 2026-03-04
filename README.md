# 📚 Bookstore – AWS CDK + Python + Vue.js

A monorepo bookstore application with:

- **Backend**: Python Lambda functions (create, search, delete books)
- **Infrastructure**: Python AWS CDK v2 (DynamoDB, API Gateway, S3, CloudFront)
- **Frontend**: Vue 3 + Vite single-page application
- **CI/CD**: GitHub Actions (test → build → deploy)

---

## Repository Structure

```
bookstore-aws-cdk-python-vuejs/
├── .github/workflows/deploy.yml   # CI/CD pipeline
├── backend/
│   ├── handlers/
│   │   ├── create_book.py         # POST /books
│   │   ├── search_books.py        # GET  /books?q=<term>
│   │   └── delete_book.py         # DELETE /books/{bookId}
│   ├── requirements.txt
│   └── tests/
│       └── test_handlers.py
├── cdk/
│   ├── app.py
│   ├── cdk.json
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── stacks/
│   │   └── bookstore_stack.py     # CDK stack definition
│   └── tests/
│       └── test_bookstore_stack.py
└── frontend/
    ├── src/
    │   ├── api.js                 # API client
    │   ├── App.vue
    │   └── components/
    │       ├── AddBook.vue        # Add book form
    │       └── BookList.vue       # Search + list + delete
    ├── package.json
    └── vite.config.js
```

---

## AWS Architecture

```
Browser ──▶ CloudFront ──▶ S3 (Vue.js SPA)
                │
                └──▶ API Gateway ──▶ Lambda (create_book)  ──▶ DynamoDB
                                 ──▶ Lambda (search_books) ──▶ DynamoDB
                                 ──▶ Lambda (delete_book)  ──▶ DynamoDB
```

### API Endpoints

| Method   | Path                | Description         |
|----------|---------------------|---------------------|
| `POST`   | `/books`            | Create a new book   |
| `GET`    | `/books?q=<term>`   | Search / list books |
| `DELETE` | `/books/{bookId}`   | Delete a book       |

---

## Prerequisites

- Python 3.12+
- Node.js 22+
- AWS CLI configured (`aws configure`)
- AWS CDK CLI: `npm install -g aws-cdk`

---

## Local Development

### Backend tests

```bash
pip install -r backend/requirements.txt boto3 moto pytest
python -m pytest backend/tests/ -v
```

### CDK tests

```bash
pip install -r cdk/requirements-dev.txt
python -m pytest cdk/tests/ -v
```

### Frontend dev server

```bash
cd frontend
npm install
# Create a local env file pointing at your deployed API
echo "VITE_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com/prod" > .env.local
npm run dev
```

---

## Deploying to AWS

### 1. Bootstrap CDK (once per account/region)

```bash
cd cdk
cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
```

### 2. Build the frontend

```bash
cd frontend
npm ci
VITE_API_URL=https://placeholder npm run build   # placeholder until first deploy
```

### 3. Deploy the CDK stack

```bash
cd cdk
cdk deploy BookstoreStack --outputs-file ../cdk-outputs.json
```

### 4. Rebuild the frontend with the real API URL

```bash
API_URL=$(jq -r '.BookstoreStack.ApiUrl' cdk-outputs.json)
cd frontend
VITE_API_URL=$API_URL npm run build
cd ../cdk
cdk deploy BookstoreStack   # sync the new frontend assets
```

The CloudFront URL is printed at the end of the deploy step.

---

## GitHub Actions CI/CD

The pipeline (`.github/workflows/deploy.yml`) runs on every push to `main`:

1. **test-backend** – pytest for Lambda handlers (moto mocks AWS)
2. **test-cdk** – CDK synth + pytest for stack assertions
3. **build-frontend** – `npm run build`
4. **deploy** – CDK deploy to AWS (production environment; OIDC auth)

### Required GitHub Secrets / Variables

| Secret                 | Description                                              |
|------------------------|----------------------------------------------------------|
| `AWS_DEPLOY_ROLE_ARN`  | IAM Role ARN for OIDC deployment (trust GitHub Actions)  |
| `AWS_ACCOUNT_ID`       | Your 12-digit AWS account ID                             |

#### IAM OIDC setup (one-time)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Then create a role that trusts the OIDC provider and attach `AdministratorAccess` (or a scoped policy). Set the ARN as `AWS_DEPLOY_ROLE_ARN`.
