import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { SpeakingRecorder } from '../ket/speaking-recorder';

class MockMediaRecorder {
  static isTypeSupported = vi.fn(() => true);
  state: RecordingState = 'inactive';
  ondataavailable: ((ev: BlobEvent) => void) | null = null;
  onstop: (() => void) | null = null;

  start() {
    this.state = 'recording';
  }

  stop() {
    this.state = 'inactive';
    if (this.ondataavailable) {
      this.ondataavailable({ data: new Blob(['audio'], { type: 'audio/webm' }) } as BlobEvent);
    }
    if (this.onstop) {
      this.onstop();
    }
  }
}

const mockGetUserMedia = vi.fn().mockResolvedValue({
  getTracks: () => [{ stop: vi.fn() }],
});

function getRecordButton() {
  return screen.getByRole('button');
}

beforeEach(() => {
  vi.clearAllMocks();
  global.MediaRecorder = MockMediaRecorder as unknown as typeof MediaRecorder;
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: { getUserMedia: mockGetUserMedia },
    writable: true,
    configurable: true,
  });
  global.URL.createObjectURL = vi.fn(() => 'blob:mock');
  global.URL.revokeObjectURL = vi.fn();
  vi.useFakeTimers({ shouldAdvanceTime: true });
});

afterEach(() => {
  vi.useRealTimers();
});

describe('SpeakingRecorder', () => {
  it('renders record button and prompt', () => {
    renderWithProviders(<SpeakingRecorder prompt="Read this sentence aloud" />);

    expect(screen.getByText('Read this sentence aloud')).toBeInTheDocument();
    expect(screen.getByText('点击开始录音')).toBeInTheDocument();
    expect(getRecordButton()).toBeInTheDocument();
  });

  it('shows default prompt when none provided', () => {
    renderWithProviders(<SpeakingRecorder />);
    expect(screen.getByText('Describe what you did last weekend.')).toBeInTheDocument();
  });

  it('starts recording when mic button is clicked', async () => {
    renderWithProviders(<SpeakingRecorder />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
      expect(screen.getByText('录音中...')).toBeInTheDocument();
    });
  });

  it('stops recording and shows playback controls when stop is clicked', async () => {
    const onSubmit = vi.fn();
    renderWithProviders(<SpeakingRecorder onSubmit={onSubmit} />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('录音中...')).toBeInTheDocument();
    });

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('点击麦克风重录')).toBeInTheDocument();
      expect(screen.getByText('播放')).toBeInTheDocument();
      expect(screen.getByText('重录')).toBeInTheDocument();
      expect(screen.getByText('提交录音')).toBeInTheDocument();
    });
  });

  it('calls onSubmit when submit button is clicked after recording', async () => {
    const onSubmit = vi.fn();
    renderWithProviders(<SpeakingRecorder onSubmit={onSubmit} />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('录音中...')).toBeInTheDocument();
    });

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('提交录音')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('提交录音'));
    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith(expect.any(Blob));
  });

  it('shows error when microphone permission denied', async () => {
    mockGetUserMedia.mockRejectedValueOnce(
      new DOMException('Permission denied', 'NotAllowedError'),
    );

    renderWithProviders(<SpeakingRecorder />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText(/麦克风权限被拒绝/)).toBeInTheDocument();
    });
  });

  it('shows timer incrementing while recording', async () => {
    renderWithProviders(<SpeakingRecorder />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('录音中...')).toBeInTheDocument();
    });

    expect(screen.getByText('0:00')).toBeInTheDocument();

    vi.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(screen.getByText('0:03')).toBeInTheDocument();
    });
  });

  it('resets recording when reset button is clicked', async () => {
    renderWithProviders(<SpeakingRecorder />);

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('录音中...')).toBeInTheDocument();
    });

    fireEvent.click(getRecordButton());

    await waitFor(() => {
      expect(screen.getByText('重录')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('重录'));

    await waitFor(() => {
      expect(screen.getByText('点击开始录音')).toBeInTheDocument();
      expect(screen.getByText('0:00')).toBeInTheDocument();
    });
  });
});
