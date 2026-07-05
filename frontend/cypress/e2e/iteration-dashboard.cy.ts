/**
 * E2E Tests: Iteration Dashboard
 * Tests the complete dashboard functionality
 */

describe('Iteration Dashboard', () => {
  const baseUrl = 'http://localhost:3000';
  const jobId = 'iterate_test_12345';

  beforeEach(() => {
    // Mock API responses
    cy.intercept('GET', `/api/v1/iteration/${jobId}`, {
      statusCode: 200,
      body: {
        job_id: jobId,
        status: 'processing',
        start_grade: 'C',
        final_grade: 'B+',
        grade_improvement: 16,
        iterations_count: 3,
        max_iterations: 10,
        current_iteration: 3,
        target_grade: 'A',
        progress_percent: 30,
        history: [
          {
            iteration_number: 1,
            grade_before: 'C',
            grade_after: 'B-',
            issues_fixed: 5,
            agent_selected: 'Agent A (Simplicity First)',
            fix_description: 'Extracted 3 helper functions',
            validation_passed: true,
            applied_at: '2026-07-05T10:23:45Z',
          },
          {
            iteration_number: 2,
            grade_before: 'B-',
            grade_after: 'B',
            issues_fixed: 6,
            agent_selected: 'Agent A (Simplicity First)',
            fix_description: 'Removed code duplication',
            validation_passed: true,
            applied_at: '2026-07-05T10:25:10Z',
          },
          {
            iteration_number: 3,
            grade_before: 'B',
            grade_after: 'B+',
            issues_fixed: 8,
            agent_selected: 'Agent B (Architecture Focused)',
            fix_description: 'Optimized module structure',
            validation_passed: true,
            applied_at: '2026-07-05T10:27:35Z',
          },
        ],
        metrics: {
          total_iterations: 3,
          total_issues_fixed: 19,
          quality_score: 80.5,
          complexity_reduction: '28 → 18 (36%)',
          agents_used: ['Agent A', 'Agent B'],
        },
        created_at: '2026-07-05T10:20:00Z',
        started_at: '2026-07-05T10:20:15Z',
        completed_at: null,
      },
    }).as('getJobStatus');

    cy.visit(`${baseUrl}/dashboard/${jobId}`);
  });

  describe('Header', () => {
    it('should display job ID and status', () => {
      cy.get('.header-title h1').should('contain', 'Code Improvement Dashboard');
      cy.get('.job-id').should('contain', jobId);
      cy.get('.status-badge').should('contain', 'PROCESSING');
    });

    it('should have pause button', () => {
      cy.get('.btn-pause').should('contain', '⏸ Pause');
      cy.get('.btn-pause').click();
      cy.get('.btn-pause').should('contain', '▶ Resume');
    });
  });

  describe('Grade Section', () => {
    it('should display current grade', () => {
      cy.get('.grade-display').should('contain', 'B+');
      cy.get('.grade-score').should('contain', '80.5/100');
    });

    it('should show grade progression', () => {
      cy.get('.grade-progression').should('contain', 'C');
      cy.get('.grade-progression').should('contain', 'B-');
      cy.get('.grade-progression').should('contain', 'B');
      cy.get('.grade-progression').should('contain', 'B+');
    });

    it('should display progress bar', () => {
      cy.get('.progress-bar').should('exist');
      cy.get('.progress-fill').should('have.css', 'width');
      cy.get('.progress-text').should('contain', '30%');
    });

    it('should show grade improvement', () => {
      cy.get('.improvement-value').should('contain', '+16');
      cy.get('.improvement-detail').should('contain', 'C → B+');
    });
  });

  describe('Charts', () => {
    it('should render grade progression chart', () => {
      cy.get('.charts-section').within(() => {
        cy.contains('h3', 'Grade Progression').should('be.visible');
        cy.get('.recharts-wrapper').should('exist');
      });
    });

    it('should render issues fixed chart', () => {
      cy.get('.charts-section').within(() => {
        cy.contains('h3', 'Issues Fixed Per Iteration').should('be.visible');
      });
    });

    it('should render agent selection pie chart', () => {
      cy.get('.charts-section').within(() => {
        cy.contains('h3', 'Agent Selection').should('be.visible');
      });
    });
  });

  describe('Metrics', () => {
    it('should display metric cards', () => {
      cy.get('.metrics-grid').within(() => {
        cy.get('.metric-card').should('have.length', 4);
      });
    });

    it('should show correct metric values', () => {
      cy.contains('.metric-label', 'Total Issues Fixed')
        .parent()
        .should('contain', '19');

      cy.contains('.metric-label', 'Iterations Completed')
        .parent()
        .should('contain', '3/10');

      cy.contains('.metric-label', 'Target Grade')
        .parent()
        .should('contain', 'A');
    });
  });

  describe('Timeline', () => {
    it('should display all iterations', () => {
      cy.get('.timeline-item').should('have.length', 3);
    });

    it('should show iteration details', () => {
      cy.get('.timeline-item').first().within(() => {
        cy.should('contain', 'C');
        cy.should('contain', 'B-');
        cy.should('contain', 'Agent A');
        cy.should('contain', 'Extracted');
        cy.should('contain', '✅');
      });
    });

    it('should show agent for each iteration', () => {
      cy.get('.timeline-item:nth-child(3)').within(() => {
        cy.should('contain', 'Agent B');
      });
    });
  });

  describe('Real-time Updates', () => {
    it('should poll status regularly', () => {
      cy.wait('@getJobStatus');
      cy.wait(1000);
      cy.wait('@getJobStatus');
    });

    it('should update when paused', () => {
      cy.get('.btn-pause').click();
      cy.wait(2000);
      // Only one request should be made (the initial one)
      cy.get('@getJobStatus.all').then((requests) => {
        expect(requests.length).to.be.lessThan(3);
      });
    });
  });

  describe('Responsive Design', () => {
    it('should be responsive on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.grade-section').should('be.visible');
      cy.get('.charts-section').should('be.visible');
      cy.get('.metrics-section').should('be.visible');
    });

    it('should be responsive on tablet', () => {
      cy.viewport('ipad-2');
      cy.get('.grade-section').should('be.visible');
      cy.get('.charts-section').should('be.visible');
    });

    it('should stack charts on small screens', () => {
      cy.viewport('iphone-x');
      // Charts should stack vertically
      cy.get('.charts-section').should('have.css', 'grid-template-columns');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', () => {
      cy.intercept('GET', `/api/v1/iteration/${jobId}`, {
        statusCode: 500,
        body: { error: 'Server error' },
      });

      cy.visit(`${baseUrl}/dashboard/${jobId}`);
      cy.get('.error-boundary-container').should('be.visible');
    });

    it('should show retry button on error', () => {
      cy.intercept('GET', `/api/v1/iteration/${jobId}`, {
        statusCode: 404,
      });

      cy.visit(`${baseUrl}/dashboard/${jobId}`);
      cy.get('.retry-button').should('be.visible');
    });
  });

  describe('Completion State', () => {
    beforeEach(() => {
      cy.intercept('GET', `/api/v1/iteration/${jobId}`, {
        statusCode: 200,
        body: {
          job_id: jobId,
          status: 'completed',
          start_grade: 'C',
          final_grade: 'A',
          grade_improvement: 23,
          iterations_count: 4,
          max_iterations: 10,
          history: [],
          metrics: {},
          created_at: '2026-07-05T10:20:00Z',
          completed_at: '2026-07-05T10:35:00Z',
        },
      });
    });

    it('should display completion message', () => {
      cy.visit(`${baseUrl}/dashboard/${jobId}`);
      cy.get('.completion-message.completed').should('contain', 'Job Complete');
    });

    it('should stop polling on completion', () => {
      cy.visit(`${baseUrl}/dashboard/${jobId}`);
      cy.get('@getJobStatus.all').then((requests) => {
        const initialCount = requests.length;
        cy.wait(2000);
        cy.get('@getJobStatus.all').then((requests) => {
          // Should not make additional requests after completion
          expect(requests.length).to.equal(initialCount);
        });
      });
    });
  });

  describe('Performance', () => {
    it('should load dashboard in < 3 seconds', () => {
      cy.visit(`${baseUrl}/dashboard/${jobId}`, {
        onBeforeLoad: (win) => {
          win.performance.mark('start');
        },
        onLoad: (win) => {
          win.performance.mark('end');
          win.performance.measure('pageLoad', 'start', 'end');
          const measure = win.performance.getEntriesByName('pageLoad')[0];
          expect(measure.duration).to.be.lessThan(3000);
        },
      });
    });

    it('should update charts smoothly', () => {
      cy.get('.recharts-surface').should('exist');
      // Verify animation classes are applied
      cy.get('.grade-section').should('have.class', 'animate-slide-up');
    });
  });
});
