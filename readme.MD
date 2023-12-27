gcloud builds submit --tag gcr.io/boxwood-airport-304120/bia_calculator  --project=boxwood-airport-304120

gcloud run deploy --image gcr.io/boxwood-airport-304120/bia_calculator --platform managed  --project=boxwood-airport-304120 --allow-unauthenticated