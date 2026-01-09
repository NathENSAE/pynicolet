%% FieldTrip Comparison for pynicolet
% This script loads the same Nicolet .e file using FieldTrip for validation.
% Requires FieldTrip to be in your MATLAB path.

%% ========================= SETUP ========================================
clc;
clear;
close all;
addpath('C:\Users\natha\AppData\Roaming\MathWorks\MATLAB Add-Ons\Collections\FieldTrip');
ft_defaults;

filename = './EEG_test_data.e';

% 1. Read Header fprintf('Reading header for: %s\n', filename);
hdr = ft_read_header(filename);

disp('FieldTrip Header Information:');
disp(hdr);

% 2. Read Data
chan_idx = 1;
data = ft_read_data(filename, 'chanindx', chan_idx);

fprintf('\nData shape (FieldTrip [channels x samples]): [%d x %d]\n', size(data, 1), size(data, 2));

% 3. Basic Stats for comparison
fprintf('Channel %d mean: %.4f\n', chan_idx, mean(data(1,:)));
fprintf('Channel %d std:  %.4f\n', chan_idx, std(data(1, :)));

% 4. Plot for visual check
figure;
plot(data(1, 1 : min(5000, end)));
title(sprintf('FieldTrip: Channel %d (First 5000 samples)', chan_idx));
xlabel('Samples');
ylabel('Amplitude');
grid on;
