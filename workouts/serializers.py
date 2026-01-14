from rest_framework import serializers
from accounts.models import User
from .models import WorkoutPlan, WorkoutTask

class WorkoutPlanSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    gym_branch_name = serializers.CharField(source="gym_branch.name", read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = ["id", "title", "description", "created_by", "created_by_email", 
                  "gym_branch", "gym_branch_name", "created_at"]
        read_only_fields = ["id", "created_by", "created_by_email", "gym_branch_name", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        
        if user.role == User.TRAINER:
            validated_data["gym_branch"] = user.gym_branch
        elif user.role == User.SUPER_ADMIN and "gym_branch" not in validated_data:
            raise serializers.ValidationError({"gym_branch": "Gym branch is required."})
        
        return super().create(validated_data)

class WorkoutTaskSerializer(serializers.ModelSerializer):
    workout_plan_title = serializers.CharField(source="workout_plan.title", read_only=True)
    member_email = serializers.EmailField(source="member.email", read_only=True)

    class Meta:
        model = WorkoutTask
        fields = ["id", "workout_plan", "workout_plan_title", "member", 
                  "member_email", "status", "due_date", "created_at"]
        read_only_fields = ["id", "workout_plan_title", "member_email", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        is_update = self.instance is not None
    
        if user.role == User.MEMBER:
            if not is_update or set(attrs.keys()) - {"status"}:
                raise serializers.ValidationError("Members can only update status of their tasks.")
            return attrs
        
        plan = attrs.get("workout_plan") or (self.instance.workout_plan if is_update else None)
        member = attrs.get("member") or (self.instance.member if is_update else None)
        
        if member and member.role != User.MEMBER:
            raise serializers.ValidationError({"member": "Can only assign to members."})
        
        if user.role == User.TRAINER:
            user_branch = user.gym_branch_id
            
            if plan and plan.gym_branch_id != user_branch:
                raise serializers.ValidationError({"workout_plan": "Plan must be from your branch."})
            if member and member.gym_branch_id != user_branch:
                raise serializers.ValidationError({"member": "Member must be from your branch."})
            
            if is_update:
                if "workout_plan" in attrs and attrs["workout_plan"] != self.instance.workout_plan:
                    raise serializers.ValidationError({"workout_plan": "Cannot change plan after creation."})
                if "member" in attrs and attrs["member"] != self.instance.member:
                    raise serializers.ValidationError({"member": "Cannot reassign task."})
        return attrs