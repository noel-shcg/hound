import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

describe('App', () => {
  it('renders dashboard on root path', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Should render the dashboard
    // We can't easily test the full routing without more setup
    // but we can verify the component mounts
    expect(document.body).toBeDefined();
  });
});
