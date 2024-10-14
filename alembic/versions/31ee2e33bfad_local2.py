"""local2

Revision ID: 31ee2e33bfad
Revises: 6a569850eb93
Create Date: 2024-10-14 17:58:15.814195

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "31ee2e33bfad"
down_revision: Union[str, None] = "6a569850eb93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("representative_name", sa.String(length=255), nullable=False),
        sa.Column("registration_number", sa.String(length=255), nullable=False),
        sa.Column("call_number", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("corporate_seal", sa.String(length=255), nullable=False),
        sa.Column("nameplate", sa.String(length=255), nullable=False),
        sa.Column("mail_address", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "salary_brackets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("minimum_hourly_rate", sa.Integer(), nullable=False),
        sa.Column("minimum_monthly_rate", sa.Integer(), nullable=False),
        sa.Column("national_pension", sa.Integer(), nullable=False),
        sa.Column("health_insurance", sa.Integer(), nullable=False),
        sa.Column("employment_insurance", sa.Integer(), nullable=False),
        sa.Column("long_term_care_insurance", sa.Integer(), nullable=False),
        sa.Column("minimun_pension_income", sa.Integer(), nullable=False),
        sa.Column("maximum_pension_income", sa.Integer(), nullable=False),
        sa.Column("maximum_national_pension", sa.Integer(), nullable=False),
        sa.Column("minimum_health_insurance", sa.Integer(), nullable=False),
        sa.Column("maximum_health_insurance", sa.Integer(), nullable=False),
        sa.Column("local_income_tax_rate", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "auto_overtime_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column(
            "role", sa.Enum("최고관리자", "관리자", name="user_role"), nullable=False
        ),
        sa.Column("is_auto_applied", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "branch_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("branch_code", sa.String(length=50), nullable=False),
        sa.Column("representative_doctor", sa.String(length=100), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("branch_name", sa.String(length=100), nullable=False),
        sa.Column("business_number", sa.String(length=20), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("seal_image_path", sa.String(length=255), nullable=True),
        sa.Column("nameplate_image_path", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_code"),
    )
    op.create_table(
        "commute_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("do_commute", sa.Boolean(), nullable=True),
        sa.Column("allowed_ip_commute", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "document_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=255), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=True),
        sa.Column("can_edit", sa.Boolean(), nullable=True),
        sa.Column("can_delete", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "holiday_work_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("do_holiday_work", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "leave_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_paid", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("leave_count", sa.Integer(), nullable=False),
        sa.Column("is_leave_of_absence", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_id", "date", name="uq_branch_date"),
    )
    op.create_index(
        "idx_leave_category_branch_id", "leave_categories", ["branch_id"], unique=False
    )
    op.create_index(
        "idx_leave_category_date", "leave_categories", ["date"], unique=False
    )
    op.create_table(
        "overtime_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("ot_30", sa.Integer(), nullable=False),
        sa.Column("ot_60", sa.Integer(), nullable=False),
        sa.Column("ot_90", sa.Integer(), nullable=False),
        sa.Column("ot_120", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "parts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("task", sa.String(length=500), nullable=True),
        sa.Column("is_doctor", sa.Boolean(), nullable=True),
        sa.Column("required_certification", sa.Boolean(), nullable=True),
        sa.Column("leave_granting_authority", sa.Boolean(), nullable=True),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rest_days",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "rest_type", sa.Enum("공휴일", "주말", name="rest_day_type"), nullable=False
        ),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_paid", sa.Boolean(), nullable=True),
        sa.Column("is_holiday_work_allowed", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("branch_id", "date", name="uq_branch_part_date"),
    )
    op.create_index("idx_rest_days_branch_id", "rest_days", ["branch_id"], unique=False)
    op.create_index("idx_rest_days_date", "rest_days", ["date"], unique=False)
    op.create_table(
        "tax_brackets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("salary_bracket_id", sa.Integer(), nullable=False),
        sa.Column("lower_limit", sa.Integer(), nullable=False),
        sa.Column("upper_limit", sa.Integer(), nullable=True),
        sa.Column("tax_rate", sa.Float(), nullable=False),
        sa.Column("deduction", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["salary_bracket_id"],
            ["salary_brackets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "allowance_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("comprehensive_overtime", sa.Boolean(), nullable=True),
        sa.Column("annual_leave", sa.Boolean(), nullable=True),
        sa.Column("holiday_work", sa.Boolean(), nullable=True),
        sa.Column("job_duty", sa.Boolean(), nullable=True),
        sa.Column("meal", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["parts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "salary_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("base_salary", sa.Integer(), nullable=True),
        sa.Column("annual_leave_days", sa.Integer(), nullable=True),
        sa.Column("sick_leave_days", sa.Integer(), nullable=True),
        sa.Column("overtime_rate", sa.Float(), nullable=True),
        sa.Column("night_work_allowance", sa.Integer(), nullable=True),
        sa.Column("holiday_work_allowance", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["parts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("education", sa.String(length=255), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("resignation_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.Enum("남자", "여자", name="user_gender"), nullable=True),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("last_company", sa.String(length=255), nullable=True),
        sa.Column("last_position", sa.String(length=255), nullable=True),
        sa.Column("last_career_start_date", sa.Date(), nullable=True),
        sa.Column("last_career_end_date", sa.Date(), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "MSO 최고권한",
                "최고관리자",
                "관리자",
                "사원",
                "퇴사자",
                name="user_role",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["branches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["parts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "work_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("weekly_work_days", sa.Integer(), nullable=False),
        sa.Column("weekday_start_time", sa.Time(), nullable=False),
        sa.Column("weekday_end_time", sa.Time(), nullable=False),
        sa.Column("weekday_is_holiday", sa.Boolean(), nullable=True),
        sa.Column("saturday_start_time", sa.Time(), nullable=True),
        sa.Column("saturday_end_time", sa.Time(), nullable=True),
        sa.Column("saturday_is_holiday", sa.Boolean(), nullable=True),
        sa.Column("sunday_start_time", sa.Time(), nullable=True),
        sa.Column("sunday_end_time", sa.Time(), nullable=True),
        sa.Column("sunday_is_holiday", sa.Boolean(), nullable=True),
        sa.Column("doctor_break_start_time", sa.Time(), nullable=True),
        sa.Column("doctor_break_end_time", sa.Time(), nullable=True),
        sa.Column("staff_break_start_time", sa.Time(), nullable=True),
        sa.Column("staff_break_end_time", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["part_id"],
            ["parts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "leave_histories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("leave_category_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_paid", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=True),
        sa.Column("is_leave_of_absence", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_yn", sa.String(length=1), nullable=True),
        sa.ForeignKeyConstraint(
            ["leave_category_id"],
            ["leave_categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_user_date"),
    )
    op.create_index("idx_leave_history_date", "leave_histories", ["date"], unique=False)
    op.create_index(
        "idx_leave_history_user_id", "leave_histories", ["user_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_leave_history_user_id", table_name="leave_histories")
    op.drop_index("idx_leave_history_date", table_name="leave_histories")
    op.drop_table("leave_histories")
    op.drop_table("work_policies")
    op.drop_table("users")
    op.drop_table("salary_policies")
    op.drop_table("allowance_policies")
    op.drop_table("tax_brackets")
    op.drop_index("idx_rest_days_date", table_name="rest_days")
    op.drop_index("idx_rest_days_branch_id", table_name="rest_days")
    op.drop_table("rest_days")
    op.drop_table("parts")
    op.drop_table("overtime_policies")
    op.drop_index("idx_leave_category_date", table_name="leave_categories")
    op.drop_index("idx_leave_category_branch_id", table_name="leave_categories")
    op.drop_table("leave_categories")
    op.drop_table("holiday_work_policies")
    op.drop_table("document_policies")
    op.drop_table("commute_policies")
    op.drop_table("branch_policies")
    op.drop_table("auto_overtime_policies")
    op.drop_table("salary_brackets")
    op.drop_table("branches")
    # ### end Alembic commands ###
