from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Auth.router import router as auth_router
from app.HR.router import router as hr_router
from app.HR.manager_router import router as manager_router
from app.Employees.router import router as employee_router  

app = FastAPI()

#CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug: Print all routes
print("Auth routes:", [route.path for route in auth_router.routes])
print("HR routes:", [route.path for route in hr_router.routes])
print("Employee routes:", [route.path for route in employee_router.routes])

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(hr_router, prefix="/hr", tags=["HR"])
app.include_router(employee_router, prefix="/employees", tags=["Employees"])
app.include_router(manager_router, prefix="/hr", tags=["Manager"])
 

@app.get("/")
def home():
    return {"message": "Welcome to the ERP System"}
print({"message": "Welcome to the ERP System"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


