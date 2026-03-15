import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
    it('renders without crashing', () => {
        render(<App />);
        // Check if the logo or a known heading is in the document
        expect(screen.getByText(/SwiftValuation AI/i)).toBeInTheDocument();
    });
});
