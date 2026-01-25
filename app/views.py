from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import QuizForm, QuestionForm, AnswerForm
from .models import Quiz, Question, Answer, UserAnswer, QuizAttempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


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


@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        for question in quiz.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')

            if answer_id:
                answer = get_object_or_404(
                    Answer,
                    id=answer_id,
                    question=question
                )

                UserAnswer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'answer': answer}
                )
            else:
                UserAnswer.objects.filter(
                    user=request.user,
                    question=question
                ).delete()

        return redirect('quiz_result', quiz_id=quiz.id)


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_questions = questions.count()

    user_answers_qs = UserAnswer.objects.filter(
        user=request.user,
        question__quiz=quiz
    ).select_related('answer')

    user_answers = {ua.question.id: ua for ua in user_answers_qs}

    correct_answers = 0
    for question in questions:
        ua = user_answers.get(question.id)
        if ua and ua.answer.is_correct:
            correct_answers += 1

    QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=correct_answers,
        total=total_questions
    )

    attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz
    )

    if attempts.count() > 10:
        for attempt in attempts[10:]:
            attempt.delete()

    recent_attempts = attempts[:10]

    return render(request, 'app/quiz_result.html', {
        'quiz': quiz,
        'score': f"{correct_answers} / {total_questions}",
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'user_answers': user_answers,
        'recent_attempts': recent_attempts,
    })



@login_required
def quiz_question(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all().order_by('id'))

    total_questions = len(questions)

    if question_number < 1 or question_number > total_questions:
        return redirect('quiz_result', quiz_id=quiz.id)

    question = questions[question_number - 1]

    
    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        if answer_id:
            answer = get_object_or_404(Answer, id=answer_id, question=question)
            UserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'answer': answer}
            )

        if question_number == total_questions:
            return redirect('quiz_result', quiz_id=quiz.id)
        else:
            return redirect(
                'quiz_question',
                quiz_id=quiz.id,
                question_number=question_number + 1
            )

    user_answer = UserAnswer.objects.filter(
        user=request.user,
        question=question
    ).first()

    return render(request, 'app/quiz_question.html', {
        'quiz': quiz,
        'question': question,
        'question_number': question_number,
        'total_questions': total_questions,
        'user_answer': user_answer,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # авто-логін після реєстрації
            return redirect('quiz_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form
    })