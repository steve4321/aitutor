import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { ChatInput } from '../chat/chat-input';

describe('ChatInput', () => {
  it('renders input field with default placeholder', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);
    expect(screen.getByPlaceholderText('输入消息...')).toBeInTheDocument();
  });

  it('renders input field with custom placeholder', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} placeholder="Ask anything" />);
    expect(screen.getByPlaceholderText('Ask anything')).toBeInTheDocument();
  });

  it('calls onSend when form submitted with text via button', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: 'Hello AI' } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(onSend).toHaveBeenCalledWith('Hello AI');
  });

  it('does not call onSend when input is empty', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(onSend).not.toHaveBeenCalled();
  });

  it('does not call onSend when input is only whitespace', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: '   ' } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(onSend).not.toHaveBeenCalled();
  });

  it('clears input after send', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    expect(textarea).toHaveValue('Hello');

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(textarea).toHaveValue('');
  });

  it('disables textarea and button when disabled prop is true', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} disabled={true} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    expect(textarea).toBeDisabled();

    const sendButton = screen.getByRole('button');
    expect(sendButton).toBeDisabled();
  });

  it('does not call onSend when disabled', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} disabled={true} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: 'Hello' } });

    const sendButton = screen.getByRole('button');
    expect(sendButton).toBeDisabled();
  });

  it('calls onSend when Enter is pressed without Shift', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    expect(onSend).toHaveBeenCalledWith('Test message');
  });

  it('does not call onSend when Shift+Enter is pressed', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(onSend).not.toHaveBeenCalled();
  });

  it('trims whitespace before sending', () => {
    const onSend = vi.fn();
    renderWithProviders(<ChatInput onSend={onSend} />);

    const textarea = screen.getByPlaceholderText('输入消息...');
    fireEvent.change(textarea, { target: { value: '  hello world  ' } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(onSend).toHaveBeenCalledWith('hello world');
  });
});
