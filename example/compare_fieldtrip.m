%% FieldTrip Comparison for pynicolet
% This script loads the entire Nicolet .e file using FieldTrip.
% It measures the time taken to read ALL channels and ALL timepoints.

%% ========================= SETUP ========================================
clc;
clear;
close all;

% Ensure FieldTrip is initialized
ft_defaults;

filename = './example/EEG_test_data.e';

%% 1. Read Header 
fprintf('Reading header for: %s\n', filename);

tic; % Start timer for header
hdr = ft_read_header(filename);
headerTime = toc; 
fprintf('Time to read header: %.4f seconds\n', headerTime);

disp('FieldTrip Header Information:');
disp(hdr);

% Optional: Read events if needed
% evt = ft_read_event(filename);

%% 2. Read ALL Data
fprintf('\nReading ALL data (all channels, all timepoints)...\n');

tic; % Start timer for full data load
% By default, calling ft_read_data without 'chanindx' reads everything
data = ft_read_data(filename); 
dataTime = toc; 

fprintf('Time to read ALL data: %.4f seconds\n', dataTime);
fprintf('Data shape (FieldTrip [channels x samples]): [%d x %d]\n', size(data, 1), size(data, 2));

%% 3. Basic Stats for comparison
% Calculate stats across the entire matrix (or you can pick a specific channel to compare)
global_mean = mean(data(:));
global_std = std(data(:));

fprintf('Global Matrix Mean: %.4f\n', global_mean);
fprintf('Global Matrix Std:  %.4f\n', global_std);