from django.db import models

class Professor(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    office = models.CharField(max_length=50)
    rating = models.FloatField(default=0.0)
    creator_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.professor.name} - {self.rating}"
