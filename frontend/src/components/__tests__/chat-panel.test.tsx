import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { ChatPanel } from '../chat/chat-panel';
import type { ChatMessage } from '@/types/problem';

describe('ChatPanel', () => {
  it('renders empty state when no messages', () => {
    renderWithProviders(<ChatPanel messages={[]} />);
    expect(screen.getByText('开始和AI老师对话吧')).toBeInTheDocument();
  });

  it('renders a list of messages', () => {
    const messages: ChatMessage[] = [
      { id: '1', role: 'user', content: 'Hello' },
      { id: '2', role: 'assistant', content: 'Hi there' },
      { id: '3', role: 'user', content: 'How are you?' },
    ];

    renderWithProviders(<ChatPanel messages={messages} />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there')).toBeInTheDocument();
    expect(screen.getByText('How are you?')).toBeInTheDocument();
    expect(screen.queryByText('开始和AI老师对话吧')).not.toBeInTheDocument();
  });

  it('applies different styles for user and assistant messages', () => {
    const messages: ChatMessage[] = [
      { id: '1', role: 'user', content: 'User msg' },
      { id: '2', role: 'assistant', content: 'Assistant msg' },
    ];

    const { container } = renderWithProviders(<ChatPanel messages={messages} />);

    const userMsg = screen.getByText('User msg');
    const assistantMsg = screen.getByText('Assistant msg');

    expect(userMsg.className).toContain('ml-auto');
    expect(assistantMsg.className).toContain('mr-auto');
  });

  it('applies custom className', () => {
    const { container } = renderWithProviders(
      <ChatPanel messages={[]} className="custom-class" />,
    );
    const panel = container.firstElementChild!;
    expect(panel.className).toContain('custom-class');
  });

  it('renders messages in order', () => {
    const messages: ChatMessage[] = [
      { id: '1', role: 'user', content: 'First' },
      { id: '2', role: 'assistant', content: 'Second' },
      { id: '3', role: 'user', content: 'Third' },
    ];

    renderWithProviders(<ChatPanel messages={messages} />);
    const rendered = screen.getAllByText(/First|Second|Third/);
    expect(rendered.map((el) => el.textContent)).toEqual(['First', 'Second', 'Third']);
  });
});
