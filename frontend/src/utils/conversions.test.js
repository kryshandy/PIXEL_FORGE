import { describe, it, expect } from 'vitest';
import { porosityPercentToFraction, metersToFeet } from './conversions';

describe('conversions', () => {
  it('convertit la porosité en pourcentage vers une fraction', () => {
    expect(porosityPercentToFraction(20)).toBeCloseTo(0.20);
  });

  it('convertit des mètres en pieds', () => {
    expect(metersToFeet(1)).toBeCloseTo(3.28084);
  });
});