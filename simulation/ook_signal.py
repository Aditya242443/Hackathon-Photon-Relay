import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

os.makedirs('plots', exist_ok=True)

# Step 1 — Generate random 50-bit message
bits = np.random.randint(0, 2, 50)

# Step 2 — Map bits to voltage (OOK: 1 → 1.0V, 0 → 0.0V)
signal = np.where(bits == 1, 1.0, 0.0)

# Step 3 — Add Gaussian noise (simulates transmission through space)
noisy = signal + np.random.normal(0, 0.3, len(signal))

# Step 4 — Threshold decode (above 0.5V = bit 1, below = bit 0)
decoded = np.where(noisy > 0.5, 1, 0)

# Step 5 — Calculate Bit Error Rate (BER)
BER = np.sum(bits != decoded) / len(bits)
print(f"Bit Error Rate (BER): {BER * 100:.2f}%")

x = np.arange(len(bits))

# Plot 1 — Clean OOK signal
plt.figure(figsize=(12, 3))
plt.step(x, signal, where='mid', color='#00C8FF', linewidth=1.5)
plt.fill_between(x, signal, step='mid', alpha=0.15, color='#00C8FF')
plt.title('Original bit stream — clean signal', fontsize=13, fontweight='bold', pad=10)
plt.xlabel('Bit Index')
plt.ylabel('Voltage (V)')
plt.ylim(-0.4, 1.4)
plt.yticks([0, 1], ['0 (OFF)', '1 (ON)'])
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('plots/plot1_clean.png', dpi=150)
plt.close()

# Plot 2 — Noisy signal after transmission
plt.figure(figsize=(12, 3))
plt.plot(x, noisy, color='#FF6B6B', linewidth=1.2, label='Noisy received signal')
plt.axhline(0.5, color='white', linestyle='--', linewidth=1, alpha=0.6, label='Decision threshold (0.5V)')
plt.fill_between(x, noisy, alpha=0.1, color='#FF6B6B')
plt.title('Received signal with noise', fontsize=13, fontweight='bold', pad=10)
plt.xlabel('Bit Index')
plt.ylabel('Voltage (V)')
plt.legend(fontsize=9)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('plots/plot2_noisy.png', dpi=150)
plt.close()

# Plot 3 — Decoded vs original
plt.figure(figsize=(12, 3))
plt.step(x, signal, where='mid', color='#00C8FF', linewidth=2, label='Original', alpha=0.8)
plt.step(x, decoded, where='mid', color='#FFD93D', linewidth=1.5,
         linestyle='--', label='Decoded', alpha=0.9)
errors = np.where(bits != decoded)[0]
plt.scatter(errors, decoded[errors], color='#FF4444', zorder=5,
            s=60, label=f'Bit errors ({len(errors)})')
plt.title(f'Decoded output — bit error rate: {BER * 100:.1f}%',
          fontsize=13, fontweight='bold', pad=10)
plt.xlabel('Bit Index')
plt.ylabel('Voltage (V)')
plt.ylim(-0.4, 1.4)
plt.yticks([0, 1], ['0', '1'])
plt.legend(fontsize=9)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('plots/plot3_decoded.png', dpi=150)
plt.close()

print("Plots saved to /plots/")
print(f"  plot1_clean.png   — Original OOK signal")
print(f"  plot2_noisy.png   — Received signal with noise")
print(f"  plot3_decoded.png — Decoded output (BER: {BER * 100:.1f}%)")