class User:
    def __init__(self,user_id,name,email,password,role):
        self.user_id=user_id
        self.name=name
        self.email=email
        self.password=password
        self.role=role
    def display_user(self):
        print("User ID:",self.user_id)
        print("Name:",self.name)
        print("Email:",self.email)
        print("Role:",self.role)