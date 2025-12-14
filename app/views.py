from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import QuizForm, QuestionForm, AnswerForm
from .models import Quiz, Question, Answer, UserAnswer


def add_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            return redirect('quiz_list')
    else:
        quiz_form = QuizForm()

    return render(request, 'app/add_quiz.html', {'quiz_form': quiz_form})


def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'app/quiz_list.html', {
        'quizzes': quizzes
    })


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('answers')

    return render(request, 'app/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions
    })


def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        for question in quiz.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                answer = get_object_or_404(Answer, id=answer_id)

                UserAnswer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'answer': answer}
                )

        return redirect('quiz_result', quiz_id=quiz.id)

    return redirect('quiz_detail', quiz_id=quiz.id)


def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__quiz=quiz
    ).select_related('answer')

    total_questions = quiz.questions.count()
    correct_answers = user_answers.filter(answer__is_correct=True).count()

    score = f"{correct_answers} / {total_questions}"

    return render(request, 'app/quiz_result.html', {
        'quiz': quiz,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'user_answers': user_answers
    })