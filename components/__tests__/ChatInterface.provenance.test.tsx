import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatMessage } from '../ChatInterface';

describe('ChatMessage provenance rendering', () => {
  it('renders provenance label when provided', () => {
    const mockMsg: any = {
      role: 'assistant',
      content: 'Full technical answer here',
      timestamp: new Date().toISOString(),
      consumerSummary: 'Short summary',
      provenance: { source: 'db', evidence_ids: [1, 2] },
      evidence: []
    };

    render(<ChatMessage message={mockMsg} />);

    // Should show the short summary
    expect(screen.getByText(/Short summary/)).toBeInTheDocument();

    // Provenance is reference-only: open the References dialog to see it
    const refsBtn = screen.getByRole('button', { name: /References/i });
    fireEvent.click(refsBtn);
    expect(screen.getByText(/Based on: db/)).toBeInTheDocument();
    expect(screen.getByText(/sources: 1,2/)).toBeInTheDocument();
  });
});
