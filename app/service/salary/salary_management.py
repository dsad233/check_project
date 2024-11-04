from fastapi import Depends


from app.cruds.salary_managment.salary_management_repo import SalaryManagementRepository

class SalaryManagementService:
    def __init__(self, salary_management_repo: SalaryManagementRepository = Depends(SalaryManagementRepository)):
        self.salary_management_repo = salary_management_repo
    
    async def get_user_salary_contract_info_by_branch(self, branch_id: int, year: int, month: int):
        return await self.salary_management_repo.get_user_salary_contract_info_by_branch(branch_id, year, month)
    