class LessonsApp {
  constructor() {
    // Elements
    this.gradeSelect = document.getElementById('gradeSelect');
    this.subjectSelect = document.getElementById('subjectSelect');
    this.lessonsGrid = document.getElementById('lessonsGrid');
    this.modal = document.getElementById('lessonModal');
    this.closeModal = document.getElementById('closeModal');
    this.lessonTitle = document.getElementById('lessonTitle');
    this.sectionTitle = document.getElementById('sectionTitle');
    this.contentArea = document.getElementById('contentArea');
    this.lessonContent = document.getElementById('lessonContent');
    this.quizView = document.getElementById('quizView');
    this.completeView = document.getElementById('completeView');
    this.readyBtn = document.getElementById('readyBtn');
    this.questionText = document.getElementById('questionText');
    this.questionCounter = document.getElementById('questionCounter');
    this.answerInput = document.getElementById('answerInput');
    this.feedback = document.getElementById('feedback');
    this.submitBtn = document.getElementById('submitBtn');
    this.nextBtn = document.getElementById('nextBtn');
    this.doubtChat = document.getElementById('doubtChat');
    this.doubtInput = document.getElementById('doubtInput');
    this.sendDoubt = document.getElementById('sendDoubt');
    this.continueBtn = document.getElementById('continueBtn');

    // State
    this.currentLesson = null;
    this.currentSection = 0;
    this.currentQuestion = 0;
    this.attempts = 0;
    this.maxAttempts = 3;
    this.startTime = null;

    this.init();
  }

  init() {
    // Load grades
    this.loadGrades();

    // Event listeners
    this.gradeSelect.addEventListener('change', () => this.onGradeChange());
    this.subjectSelect.addEventListener('change', () => this.onSubjectChange());
    this.closeModal.addEventListener('click', () => this.hideModal());
    this.readyBtn.addEventListener('click', () => this.startQuiz());
    this.submitBtn.addEventListener('click', () => this.submitAnswer());
    this.nextBtn.addEventListener('click', () => this.nextQuestion());
    this.sendDoubt.addEventListener('click', () => this.sendDoubtMessage());
    this.continueBtn.addEventListener('click', () => this.hideModal());

    // Enter to send doubt
    this.doubtInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendDoubtMessage();
      }
    });

    // Enter to submit answer
    this.answerInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.submitAnswer();
      }
    });

    // Close modal on backdrop click
    this.modal.querySelector('.modal-backdrop').addEventListener('click', () => this.hideModal());
  }

  async loadGrades() {
    try {
      const res = await fetch('/api/lessons/grades');
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        this.gradeSelect.innerHTML = '<option value="">Select Grade</option>';
        data.data.grades.forEach(grade => {
          const option = document.createElement('option');
          option.value = grade.id;
          option.textContent = grade.name;
          this.gradeSelect.appendChild(option);
        });
      }
    } catch (err) {
      console.error('Failed to load grades:', err);
    }
  }

  async onGradeChange() {
    const grade = this.gradeSelect.value;
    
    if (!grade) {
      this.subjectSelect.disabled = true;
      this.subjectSelect.innerHTML = '<option value="">Select Grade First</option>';
      this.showEmptyState();
      return;
    }

    try {
      const res = await fetch(`/api/lessons/${grade}/subjects`);
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        this.subjectSelect.disabled = false;
        this.subjectSelect.innerHTML = '<option value="">Select Subject</option>';
        data.data.subjects.forEach(subject => {
          const option = document.createElement('option');
          option.value = subject.id;
          option.textContent = subject.name;
          this.subjectSelect.appendChild(option);
        });
      }
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
    
    this.showEmptyState();
  }

  async onSubjectChange() {
    const grade = this.gradeSelect.value;
    const subject = this.subjectSelect.value;
    
    if (!grade || !subject) {
      this.showEmptyState();
      return;
    }

    try {
      const res = await fetch(`/api/lessons/${grade}/${subject}`);
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        this.renderLessons(data.data.lessons, grade, subject);
      }
    } catch (err) {
      console.error('Failed to load lessons:', err);
    }
  }

  showEmptyState() {
    this.lessonsGrid.innerHTML = `
      <div class="empty-state">
        <h3>📚 Select a grade and subject to start learning</h3>
        <p class="text-secondary">Choose your grade level and subject to see available lessons</p>
      </div>
    `;
  }

  renderLessons(lessons, grade, subject) {
    if (lessons.length === 0) {
      this.lessonsGrid.innerHTML = `
        <div class="empty-state">
          <h3>No lessons available</h3>
          <p class="text-secondary">Check back soon for new content!</p>
        </div>
      `;
      return;
    }

    this.lessonsGrid.innerHTML = '';
    lessons.forEach(lesson => {
      const card = document.createElement('div');
      card.className = 'lesson-card';
      card.innerHTML = `
        <h3>${lesson.title}</h3>
        <p>${lesson.description || 'Click to start learning'}</p>
        <div class="lesson-meta">
          <span>📖 ${lesson.sections || 0} sections</span>
        </div>
      `;
      card.addEventListener('click', () => this.openLesson(grade, subject, lesson.id));
      this.lessonsGrid.appendChild(card);
    });
  }

  async openLesson(grade, subject, lessonId) {
    try {
      const res = await fetch(`/api/lessons/${grade}/${subject}/${lessonId}`);
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        this.currentLesson = { grade, subject, id: lessonId, data: data.data.lesson };
        
        // Check for saved progress
        const progress = this.getProgress(lessonId);
        const startSectionIdx = progress && !progress.completed ? progress.currentSection : 0;
        
        this.currentSection = startSectionIdx;
        this.startTime = Date.now();
        this.loadSection(this.currentLesson.data.sections[startSectionIdx].id);
        this.showModal();
      }
    } catch (err) {
      console.error('Failed to load lesson:', err);
    }
  }

  async loadSection(sectionId) {
    const { grade, subject, id } = this.currentLesson;
    
    try {
      const res = await fetch(`/api/lessons/${grade}/${subject}/${id}/section/${sectionId}`);
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        // Find section index for display
        const sectionIdx = this.currentLesson.data.sections.findIndex(s => s.id === sectionId);
        this.currentSection = sectionIdx;
        
        this.lessonTitle.textContent = this.currentLesson.data.title;
        this.sectionTitle.textContent = `Section ${sectionIdx + 1}`;
        this.contentArea.innerHTML = this.formatContent(data.data.section.content);
        
        // Show lesson content view
        this.lessonContent.style.display = 'block';
        this.quizView.style.display = 'none';
        this.completeView.style.display = 'none';
        
        // Show doubt chat panel for content sections
        document.querySelector('.right-pane').style.display = 'flex';
        document.querySelector('.left-pane').style.flex = '3';
        document.querySelector('.left-pane').style.borderRight = '1px solid var(--border-color)';
        
        // Reset doubt chat
        this.clearDoubtChat();
      }
    } catch (err) {
      console.error('Failed to load section:', err);
    }
  }

  formatContent(content) {
    if (typeof content === 'string') {
      // Convert markdown-style formatting to HTML
      return content
        // Bold: **text** -> <strong>text</strong>
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // Italic: *text* -> <em>text</em>
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        // Bullet lists: - item -> <li>item</li>
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        // Wrap consecutive <li> in <ul>
        .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
        // Paragraphs: double newline
        .split('\n\n')
        .map(para => {
          if (para.includes('<ul>') || para.includes('<strong>')) {
            return para;
          }
          return `<p>${para.replace(/\n/g, '<br>')}</p>`;
        })
        .join('');
    }
    return content;
  }

  startQuiz() {
    const section = this.currentLesson.data.sections[this.currentSection];
    
    if (!section.questions || section.questions.length === 0) {
      // No quiz, move to next section or complete
      this.currentSection++;
      if (this.currentSection < this.currentLesson.data.sections.length) {
        const nextSection = this.currentLesson.data.sections[this.currentSection];
        this.loadSection(nextSection.id);
      } else {
        this.showCompletion();
      }
      return;
    }

    this.currentQuestion = 0;
    this.lessonContent.style.display = 'none';
    this.quizView.style.display = 'block';
    
    // Hide doubt chat panel during quiz
    document.querySelector('.right-pane').style.display = 'none';
    document.querySelector('.left-pane').style.flex = '1';
    document.querySelector('.left-pane').style.borderRight = 'none';
    
    this.loadQuestion();
  }

  loadQuestion() {
    const section = this.currentLesson.data.sections[this.currentSection];
    const question = section.questions[this.currentQuestion];
    
    this.questionText.textContent = question.question;
    this.questionCounter.textContent = `Question ${this.currentQuestion + 1} of ${section.questions.length}`;
    this.answerInput.value = '';
    this.answerInput.disabled = false;
    this.feedback.style.display = 'none';
    this.nextBtn.style.display = 'none';
    this.submitBtn.style.display = 'inline-block';
    this.attempts = 0;
  }

  async submitAnswer() {
    const section = this.currentLesson.data.sections[this.currentSection];
    const question = section.questions[this.currentQuestion];
    const userAnswer = this.answerInput.value.trim();
    
    if (!userAnswer) return;

    this.attempts++;
    
    try {
      const res = await fetch('/api/lessons/evaluate-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          grade: this.currentLesson.grade,
          subject: this.currentLesson.subject,
          lesson_id: this.currentLesson.id,
          section_id: section.id,
          question_id: question.id,
          answer: userAnswer,
          use_ai: false
        })
      });
      
      const data = await res.json();
      
      if (data.code === 0 && data.data && data.data.evaluation) {
        if (data.data.evaluation.is_correct) {
          this.showFeedback('success', '✓ Correct! Well done!');
          this.submitBtn.style.display = 'none';
          this.nextBtn.style.display = 'inline-block';
        } else {
          // Wrong answer - automatically get AI hint
          await this.getAutoHint(userAnswer);
        }
      }
    } catch (err) {
      console.error('Failed to evaluate answer:', err);
    }
  }

  async getAutoHint(userAnswer) {
    const section = this.currentLesson.data.sections[this.currentSection];
    const question = section.questions[this.currentQuestion];
    
    try {
      const res = await fetch('/api/lessons/get-hint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          grade: this.currentLesson.grade,
          subject: this.currentLesson.subject,
          lesson_id: this.currentLesson.id,
          section_id: section.id,
          question_id: question.id,
          hint_level: this.attempts,
          answer: userAnswer
        })
      });
      
      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        if (data.data.close_quiz) {
          // Answer completely wrong - close quiz and restart section
          this.showFeedback('error', `❌ ${data.data.hint}\n\nPlease review the material and try again.`);
          this.submitBtn.style.display = 'none';
          this.answerInput.disabled = true;
          
          // Show button to restart section
          setTimeout(() => {
            this.hideModal();
          }, 3000);
        } else if (this.attempts >= this.maxAttempts) {
          // Max attempts reached
          this.showFeedback('error', `Incorrect. The correct answer is: ${question.answer}`);
          this.submitBtn.style.display = 'none';
          this.nextBtn.style.display = 'inline-block';
        } else {
          // Show hint and allow retry
          this.showFeedback('warning', `💡 ${data.data.hint}\n\nTry again! (Attempt ${this.attempts}/${this.maxAttempts})`);
        }
      }
    } catch (err) {
      console.error('Failed to get hint:', err);
    }
  }

  showFeedback(type, message) {
    this.feedback.className = `feedback ${type} mt-2`;
    this.feedback.textContent = message;
    this.feedback.style.display = 'block';
  }

  nextQuestion() {
    const section = this.currentLesson.data.sections[this.currentSection];
    this.currentQuestion++;
    
    if (this.currentQuestion < section.questions.length) {
      this.loadQuestion();
    } else {
      // Section complete, move to next or finish
      this.currentSection++;
      this.saveProgress(); // Save after completing section
      
      if (this.currentSection < this.currentLesson.data.sections.length) {
        const nextSection = this.currentLesson.data.sections[this.currentSection];
        this.loadSection(nextSection.id);
      } else {
        this.showCompletion();
      }
    }
  }

  async showCompletion() {
    const elapsed = Math.round((Date.now() - this.startTime) / 60000);
    
    document.getElementById('timeSpent').textContent = `${elapsed}m`;
    document.getElementById('sectionsComplete').textContent = this.currentLesson.data.sections.length;
    
    this.lessonContent.style.display = 'none';
    this.quizView.style.display = 'none';
    this.completeView.style.display = 'block';
    
    // Hide doubt chat on completion screen too
    document.querySelector('.right-pane').style.display = 'none';
    document.querySelector('.left-pane').style.flex = '1';
    document.querySelector('.left-pane').style.borderRight = 'none';
    
    // Mark as completed in localStorage
    const progress = {
      lessonId: this.currentLesson.id,
      currentSection: this.currentLesson.data.sections.length,
      completed: true,
      completedAt: Date.now()
    };
    localStorage.setItem(`lesson_progress_${this.currentLesson.id}`, JSON.stringify(progress));
    
    // Save progress to backend
    try {
      await fetch('/api/progress/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: this.currentLesson.id,
          grade: this.currentLesson.grade,
          subject: this.currentLesson.subject,
          completed: true
        })
      });
    } catch (err) {
      console.error('Failed to save progress:', err);
    }
  }

  async sendDoubtMessage() {
    const text = this.doubtInput.value.trim();
    if (!text) return;

    this.addDoubtMessage('user', text);
    this.doubtInput.value = '';

    try {
      const section = this.currentLesson.data.sections[this.currentSection];
      
      const res = await fetch('/api/lessons/doubt-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          grade: this.currentLesson.grade,
          subject: this.currentLesson.subject,
          lesson_id: this.currentLesson.id,
          section_id: section.id
        })
      });

      const data = await res.json();
      
      if (data.code === 0 && data.data) {
        this.addDoubtMessage('assistant', data.data.response);
      } else {
        this.addDoubtMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      }
    } catch (err) {
      console.error('Failed to send doubt:', err);
      this.addDoubtMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    }
  }

  addDoubtMessage(role, text) {
    const msg = document.createElement('div');
    msg.className = `doubt-message ${role}`;
    msg.innerHTML = `<p>${text}</p>`;
    this.doubtChat.appendChild(msg);
    this.doubtChat.scrollTop = this.doubtChat.scrollHeight;
  }

  clearDoubtChat() {
    this.doubtChat.innerHTML = `
      <div class="chat-welcome">
        <p class="text-secondary">Have questions? Ask me anything about this lesson!</p>
      </div>
    `;
  }

  showModal() {
    this.modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
  }

  hideModal() {
    this.modal.style.display = 'none';
    document.body.style.overflow = '';
    
    // Save progress before closing
    if (this.currentLesson) {
      this.saveProgress();
    }
    
    this.currentLesson = null;
  }

  saveProgress() {
    const progress = {
      lessonId: this.currentLesson.id,
      currentSection: this.currentSection,
      completed: false,
      lastAccessed: Date.now()
    };
    localStorage.setItem(`lesson_progress_${this.currentLesson.id}`, JSON.stringify(progress));
  }

  getProgress(lessonId) {
    const stored = localStorage.getItem(`lesson_progress_${lessonId}`);
    return stored ? JSON.parse(stored) : null;
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  new LessonsApp();
});
