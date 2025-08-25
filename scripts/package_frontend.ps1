mkdir dist -Force
rm dist/* -r -Force

# Python
poetry install
poetry export -o dist/requirements.txt
cp *.py dist -Force
cp backend dist -r -Force

cp routes.json dist -Force

# Node
cd frontend
npm install
npm run build
