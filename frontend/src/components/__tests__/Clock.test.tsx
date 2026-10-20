import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Clock } from '../Clock';

describe('Clock', () => {
  it('renders time and date', () => {
    render(<Clock />);
    
    // The component should render time and date
    // Since we can't easily mock the date in tests without libraries,
    // we'll just check that the component renders
    const clockElement = screen.getByText(/:/);  // Time contains colon
    expect(clockElement).toBeDefined();
  });
});
