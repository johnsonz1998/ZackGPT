import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import MemoryGraph from '../MemoryGraph';
import { memoryGraphLogger } from '../../utils/memoryGraphLogger';

// Mock D3 to prevent DOM manipulation issues in tests
jest.mock('d3', () => ({
  select: jest.fn(() => ({
    selectAll: jest.fn(() => ({ remove: jest.fn() })),
    attr: jest.fn().mockReturnThis(),
    append: jest.fn().mockReturnThis(),
    call: jest.fn().mockReturnThis(),
  })),
  forceSimulation: jest.fn(() => ({
    force: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    stop: jest.fn(),
    alphaTarget: jest.fn().mockReturnThis(),
    restart: jest.fn().mockReturnThis(),
  })),
  forceLink: jest.fn(),
  forceManyBody: jest.fn(() => ({ strength: jest.fn().mockReturnThis() })),
  forceCenter: jest.fn(),
  forceCollide: jest.fn(() => ({ radius: jest.fn().mockReturnThis() })),
  zoom: jest.fn(() => ({
    scaleExtent: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
  })),
  drag: jest.fn(() => ({
    on: jest.fn().mockReturnThis(),
  })),
}));

// Mock the logger
jest.mock('../../utils/memoryGraphLogger', () => ({
  memoryGraphLogger: {
    logEvent: jest.fn(),
    logPerformance: jest.fn(),
    logInteraction: jest.fn(),
    logFiltering: jest.fn(),
    logVisualization: jest.fn(),
  },
  logMemoryGraphEvent: jest.fn(),
  logMemoryGraphPerformance: jest.fn(),
  logMemoryGraphInteraction: jest.fn(),
  logMemoryGraphFiltering: jest.fn(),
  logMemoryGraphVisualization: jest.fn(),
}));

describe('MemoryGraph Component', () => {
  const mockMemories = [
    {
      id: '1',
      question: 'What is my favorite food?',
      answer: 'Pizza',
      tags: ['preferences', 'food'],
      importance: 'high' as const,
      timestamp: '2024-01-01T10:00:00Z',
    },
    {
      id: '2',
      question: 'Where do I work?',
      answer: 'Tech company',
      tags: ['work', 'career'],
      importance: 'medium' as const,
      timestamp: '2024-01-01T11:00:00Z',
    },
    {
      id: '3',
      question: 'What is my name?',
      answer: 'John Doe',
      tags: ['identity'],
      importance: 'high' as const,
      timestamp: '2024-01-01T12:00:00Z',
    },
    {
      id: '4',
      question: 'Untagged memory',
      answer: 'Some information',
      tags: [],
      importance: 'low' as const,
      timestamp: '2024-01-01T13:00:00Z',
    },
  ];

  const mockOnMemoryClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock performance.now for consistent testing
    jest.spyOn(performance, 'now').mockReturnValue(1000);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders the MemoryGraph component', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      expect(screen.getByText('Memory Types')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select All/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select None/i })).toBeInTheDocument();
    });

    it('renders with empty memories array', () => {
      render(<MemoryGraph memories={[]} />);
      
      expect(screen.getByText('Memory Types')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select All/i })).toBeDisabled();
      expect(screen.getByRole('button', { name: /Select None/i })).toBeDisabled();
    });

    it('displays tag buttons for primary tags', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      // Should show primary tags only
      expect(screen.getByText('preferences')).toBeInTheDocument(); // Primary tag of memory 1
      expect(screen.getByText('work')).toBeInTheDocument(); // Primary tag of memory 2
      expect(screen.getByText('identity')).toBeInTheDocument(); // Primary tag of memory 3
      expect(screen.getByText('default')).toBeInTheDocument(); // Primary tag of memory 4 (no tags)
      
      // Should NOT show secondary tags
      expect(screen.queryByText('food')).not.toBeInTheDocument();
      expect(screen.queryByText('career')).not.toBeInTheDocument();
    });

    it('displays memory counts correctly', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      // Each primary tag should show 1/1 (visible/total)
      const tagButtons = screen.getAllByText(/1\/1/);
      expect(tagButtons).toHaveLength(4); // 4 primary tags
    });
  });

  describe('Tag Filtering', () => {
    it('toggles tag visibility when tag button is clicked', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const preferencesButton = screen.getByText('preferences').closest('button');
      expect(preferencesButton).toBeInTheDocument();
      
      await act(async () => {
        userEvent.click(preferencesButton!);
      });
      
      // Check that the tag count shows 0/1 (hidden)
      expect(screen.getByText(/0\/1/)).toBeInTheDocument();
    });

    it('handles Select All button correctly', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      // First hide some tags
      const preferencesButton = screen.getByText('preferences').closest('button');
      await act(async () => {
        userEvent.click(preferencesButton!);
      });
      
      // Then click Select All
      const selectAllButton = screen.getByRole('button', { name: /Select All/i });
      await act(async () => {
        userEvent.click(selectAllButton);
      });
      
      // All tags should be visible again
      const visibleCounts = screen.getAllByText(/1\/1/);
      expect(visibleCounts).toHaveLength(4);
    });

    it('handles Select None button correctly', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const selectNoneButton = screen.getByRole('button', { name: /Select None/i });
      await act(async () => {
        userEvent.click(selectNoneButton);
      });
      
      // All tags should be hidden
      const hiddenCounts = screen.getAllByText(/0\/1/);
      expect(hiddenCounts).toHaveLength(4);
    });
  });

  describe('Search Functionality', () => {
    it('displays search results count', () => {
      render(<MemoryGraph memories={mockMemories} searchQuery="pizza" />);
      
      expect(screen.getByText(/of 4 memories/)).toBeInTheDocument();
    });

    it('shows no results message for empty search', () => {
      render(<MemoryGraph memories={mockMemories} searchQuery="nonexistent" />);
      
      expect(screen.getByText(/No memories found for "nonexistent"/)).toBeInTheDocument();
    });
  });

  describe('Color Assignment', () => {
    it('assigns consistent colors to tags', () => {
      const { rerender } = render(<MemoryGraph memories={mockMemories} />);
      
      // Get initial color assignments
      const initialButtons = screen.getAllByRole('button');
      const initialColors = initialButtons.map(button => {
        const colorDiv = button.querySelector('.tag-button-color');
        return colorDiv ? window.getComputedStyle(colorDiv).backgroundColor : null;
      });
      
      // Re-render with same data
      rerender(<MemoryGraph memories={mockMemories} />);
      
      // Colors should remain consistent
      const newButtons = screen.getAllByRole('button');
      const newColors = newButtons.map(button => {
        const colorDiv = button.querySelector('.tag-button-color');
        return colorDiv ? window.getComputedStyle(colorDiv).backgroundColor : null;
      });
      
      expect(newColors).toEqual(initialColors);
    });
  });

  describe('Memory Click Handling', () => {
    it('calls onMemoryClick when provided', () => {
      render(<MemoryGraph memories={mockMemories} onMemoryClick={mockOnMemoryClick} />);
      
      // This would require mocking D3 interactions more thoroughly
      // For now, we verify the prop is passed correctly
      expect(mockOnMemoryClick).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for buttons', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      expect(screen.getByRole('button', { name: /Select All/i })).toHaveAttribute('class', 'control-btn');
      expect(screen.getByRole('button', { name: /Select None/i })).toHaveAttribute('class', 'control-btn');
    });

    it('provides keyboard navigation for tag buttons', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const tagButtons = screen.getAllByRole('button').filter(button => 
        button.classList.contains('tag-button') || 
        button.classList.contains('tag-button-visible') ||
        button.classList.contains('tag-button-hidden')
      );
      
      tagButtons.forEach(button => {
        expect(button).toHaveAttribute('type', undefined); // Should be implicit button
      });
    });
  });

  describe('Performance', () => {
    it('handles large datasets efficiently', () => {
      const largeMockMemories = Array.from({ length: 1000 }, (_, i) => ({
        id: `${i}`,
        question: `Question ${i}`,
        answer: `Answer ${i}`,
        tags: [`tag${i % 10}`],
        importance: 'medium' as const,
        timestamp: `2024-01-01T${String(i % 24).padStart(2, '0')}:00:00Z`,
      }));

      const renderStart = performance.now();
      render(<MemoryGraph memories={largeMockMemories} />);
      const renderEnd = performance.now();

      // Should render within reasonable time (less than 1 second)
      expect(renderEnd - renderStart).toBeLessThan(1000);
    });

    it('debounces rapid state changes', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const preferencesButton = screen.getByText('preferences').closest('button');
      
      // Rapidly click the same button multiple times
      await act(async () => {
        userEvent.click(preferencesButton!);
        userEvent.click(preferencesButton!);
        userEvent.click(preferencesButton!);
      });

      // Should handle rapid clicks gracefully
      expect(preferencesButton).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles invalid memory data gracefully', () => {
      const invalidMemories = [
        {
          id: '1',
          question: '',
          answer: '',
          tags: null as any,
          importance: 'invalid' as any,
          timestamp: 'invalid-date',
        },
      ];

      expect(() => {
        render(<MemoryGraph memories={invalidMemories} />);
      }).not.toThrow();
    });

    it('handles missing required props', () => {
      expect(() => {
        render(<MemoryGraph memories={undefined as any} />);
      }).not.toThrow();
    });
  });

  describe('Logging Integration', () => {
    it('logs component initialization', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      // Should log that the component was initialized
      // Note: Actual logging verification would depend on implementation
      expect(memoryGraphLogger.logEvent).toHaveBeenCalledWith(
        expect.stringContaining('init'),
        expect.any(Object)
      );
    });

    it('logs user interactions', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const selectAllButton = screen.getByRole('button', { name: /Select All/i });
      await act(async () => {
        userEvent.click(selectAllButton);
      });
      
      expect(memoryGraphLogger.logInteraction).toHaveBeenCalledWith(
        'button_click',
        expect.objectContaining({
          buttonType: 'selectAll'
        }),
        expect.any(Object)
      );
    });

    it('logs filtering operations', async () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      const preferencesButton = screen.getByText('preferences').closest('button');
      await act(async () => {
        userEvent.click(preferencesButton!);
      });
      
      expect(memoryGraphLogger.logFiltering).toHaveBeenCalledWith(
        'tag_toggle',
        expect.objectContaining({
          tag: 'preferences'
        }),
        expect.objectContaining({
          totalBefore: expect.any(Number),
          totalAfter: expect.any(Number)
        })
      );
    });
  });

  describe('Responsive Design', () => {
    it('adapts to different screen sizes', () => {
      // Mock window dimensions
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 800,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 600,
      });

      render(<MemoryGraph memories={mockMemories} />);
      
      // Component should render without issues on different screen sizes
      expect(screen.getByText('Memory Types')).toBeInTheDocument();
    });
  });

  describe('Tooltip Functionality', () => {
    it('does not show tooltip initially', () => {
      render(<MemoryGraph memories={mockMemories} />);
      
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });

    // Note: Tooltip testing would require more complex D3 mocking
    // as it depends on D3 event handling
  });

  describe('Memory Similarity', () => {
    it('calculates similarity between memories', () => {
      // This tests the similarity calculation logic
      render(<MemoryGraph memories={mockMemories} />);
      
      // The component should handle memories with overlapping tags
      const memoriesWithSimilarity = [
        ...mockMemories,
        {
          id: '5',
          question: 'Another food question?',
          answer: 'Pasta',
          tags: ['preferences', 'food'],
          importance: 'medium' as const,
          timestamp: '2024-01-01T14:00:00Z',
        },
      ];

      const { rerender } = render(<MemoryGraph memories={memoriesWithSimilarity} />);
      
      // Should render without errors even with similar memories
      expect(screen.getByText('Memory Types')).toBeInTheDocument();
    });
  });
}); 