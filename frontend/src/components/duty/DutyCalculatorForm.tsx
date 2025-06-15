import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { FiCalendar, FiDollarSign, FiHash, FiMapPin, FiPackage } from 'react-icons/fi';
import { format } from 'date-fns';
import type { DutyCalculationRequest } from '../../types';

interface DutyCalculatorFormProps {
  onSubmit: (data: DutyCalculationRequest) => void;
  isLoading?: boolean;
}

interface FormData {
  hs_code: string;
  country_code: string;
  customs_value: string;
  quantity: string;
  calculation_date: string;
}

const MAJOR_TRADING_PARTNERS = [
  { code: 'CHN', name: 'China', flag: '🇨🇳' },
  { code: 'USA', name: 'United States', flag: '🇺🇸' },
  { code: 'JPN', name: 'Japan', flag: '🇯🇵' },
  { code: 'KOR', name: 'South Korea', flag: '🇰🇷' },
  { code: 'GBR', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'DEU', name: 'Germany', flag: '🇩🇪' },
  { code: 'IND', name: 'India', flag: '🇮🇳' },
  { code: 'THA', name: 'Thailand', flag: '🇹🇭' },
  { code: 'SGP', name: 'Singapore', flag: '🇸🇬' },
  { code: 'MYS', name: 'Malaysia', flag: '🇲🇾' },
  { code: 'IDN', name: 'Indonesia', flag: '🇮🇩' },
  { code: 'VNM', name: 'Vietnam', flag: '🇻🇳' },
  { code: 'NZL', name: 'New Zealand', flag: '🇳🇿' },
  { code: 'CAN', name: 'Canada', flag: '🇨🇦' },
  { code: 'FRA', name: 'France', flag: '🇫🇷' },
  { code: 'ITA', name: 'Italy', flag: '🇮🇹' },
  { code: 'BRA', name: 'Brazil', flag: '🇧🇷' },
  { code: 'MEX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'TWN', name: 'Taiwan', flag: '🇹🇼' },
  { code: 'HKG', name: 'Hong Kong', flag: '🇭🇰' },
];

const QUANTITY_UNITS = [
  { value: 'pieces', label: 'Pieces' },
  { value: 'kg', label: 'Kilograms' },
  { value: 'litres', label: 'Litres' },
  { value: 'metres', label: 'Metres' },
  { value: 'square_metres', label: 'Square Metres' },
  { value: 'cubic_metres', label: 'Cubic Metres' },
  { value: 'pairs', label: 'Pairs' },
  { value: 'dozens', label: 'Dozens' },
];

const DutyCalculatorForm: React.FC<DutyCalculatorFormProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormData>({
    defaultValues: {
      hs_code: '',
      country_code: '',
      customs_value: '',
      quantity: '1',
      calculation_date: format(new Date(), 'yyyy-MM-dd'),
    },
  });

  const formatCurrency = (value: string) => {
    // Remove non-numeric characters except decimal point
    const numericValue = value.replace(/[^0-9.]/g, '');
    
    // Parse as number and format with commas
    const number = parseFloat(numericValue);
    if (isNaN(number)) return '';
    
    return number.toLocaleString('en-AU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const handleCurrencyChange = (value: string, onChange: (value: string) => void) => {
    // Store the raw numeric value
    const numericValue = value.replace(/[^0-9.]/g, '');
    onChange(numericValue);
  };

  const validateHsCode = (value: string) => {
    if (!value) return 'HS Code is required';
    
    // Remove dots and spaces for validation
    const cleanCode = value.replace(/[.\s]/g, '');
    
    if (!/^\d{8,10}$/.test(cleanCode)) {
      return 'HS Code must be 8-10 digits';
    }
    
    return true;
  };

  const validateCurrency = (value: string) => {
    if (!value) return 'Customs value is required';
    
    const numericValue = parseFloat(value);
    if (isNaN(numericValue) || numericValue <= 0) {
      return 'Customs value must be a positive number';
    }
    
    return true;
  };

  const validateQuantity = (value: string) => {
    if (!value) return 'Quantity is required';
    
    const numericValue = parseFloat(value);
    if (isNaN(numericValue) || numericValue <= 0) {
      return 'Quantity must be a positive number';
    }
    
    return true;
  };

  const handleFormSubmit = (data: FormData) => {
    const submissionData: DutyCalculationRequest = {
      hs_code: data.hs_code.replace(/[.\s]/g, ''), // Clean HS code
      country_code: data.country_code,
      customs_value: parseFloat(data.customs_value),
      quantity: parseFloat(data.quantity),
      calculation_date: data.calculation_date,
    };
    
    onSubmit(submissionData);
  };

  const watchedHsCode = watch('hs_code');
  const watchedCountry = watch('country_code');
  const watchedValue = watch('customs_value');

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Duty Calculator</h2>
        <p className="text-gray-600">
          Calculate import duties and taxes for goods entering Australia
        </p>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        {/* HS Code Input */}
        <div>
          <label htmlFor="hs_code" className="block text-sm font-medium text-gray-700 mb-2">
            <FiHash className="inline mr-2" />
            HS Code *
          </label>
          <Controller
            name="hs_code"
            control={control}
            rules={{ validate: validateHsCode }}
            render={({ field }) => (
              <div className="relative">
                <input
                  {...field}
                  type="text"
                  id="hs_code"
                  placeholder="e.g., 8471.30.00 or 847130"
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    errors.hs_code ? 'border-red-500' : 'border-gray-300'
                  }`}
                  maxLength={12}
                />
                {watchedHsCode && (
                  <div className="absolute right-3 top-3 text-sm text-gray-500">
                    {watchedHsCode.replace(/[.\s]/g, '').length}/10
                  </div>
                )}
              </div>
            )}
          />
          {errors.hs_code && (
            <p className="mt-1 text-sm text-red-600">{errors.hs_code.message}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Enter the 8-10 digit Harmonized System code for your product
          </p>
        </div>

        {/* Country of Origin */}
        <div>
          <label htmlFor="country_code" className="block text-sm font-medium text-gray-700 mb-2">
            <FiMapPin className="inline mr-2" />
            Country of Origin *
          </label>
          <Controller
            name="country_code"
            control={control}
            rules={{ required: 'Country of origin is required' }}
            render={({ field }) => (
              <select
                {...field}
                id="country_code"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.country_code ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select country of origin</option>
                {MAJOR_TRADING_PARTNERS.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.flag} {country.name}
                  </option>
                ))}
              </select>
            )}
          />
          {errors.country_code && (
            <p className="mt-1 text-sm text-red-600">{errors.country_code.message}</p>
          )}
          {watchedCountry && (
            <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
              <strong>FTA Status:</strong> Australia has trade agreements with many countries. 
              Preferential rates may apply.
            </div>
          )}
        </div>

        {/* Customs Value */}
        <div>
          <label htmlFor="customs_value" className="block text-sm font-medium text-gray-700 mb-2">
            <FiDollarSign className="inline mr-2" />
            Customs Value (AUD) *
          </label>
          <Controller
            name="customs_value"
            control={control}
            rules={{ validate: validateCurrency }}
            render={({ field }) => (
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="text-gray-500 sm:text-sm">$</span>
                </div>
                <input
                  {...field}
                  type="text"
                  id="customs_value"
                  placeholder="0.00"
                  className={`w-full pl-8 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    errors.customs_value ? 'border-red-500' : 'border-gray-300'
                  }`}
                  onChange={(e) => handleCurrencyChange(e.target.value, field.onChange)}
                  value={field.value ? formatCurrency(field.value) : ''}
                />
              </div>
            )}
          />
          {errors.customs_value && (
            <p className="mt-1 text-sm text-red-600">{errors.customs_value.message}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            The transaction value of the goods in Australian dollars
          </p>
        </div>

        {/* Quantity */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
              <FiPackage className="inline mr-2" />
              Quantity *
            </label>
            <Controller
              name="quantity"
              control={control}
              rules={{ validate: validateQuantity }}
              render={({ field }) => (
                <input
                  {...field}
                  type="number"
                  id="quantity"
                  min="0.01"
                  step="0.01"
                  placeholder="1"
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    errors.quantity ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
              )}
            />
            {errors.quantity && (
              <p className="mt-1 text-sm text-red-600">{errors.quantity.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="unit" className="block text-sm font-medium text-gray-700 mb-2">
              Unit
            </label>
            <select
              id="unit"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              defaultValue="pieces"
            >
              {QUANTITY_UNITS.map((unit) => (
                <option key={unit.value} value={unit.value}>
                  {unit.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Calculation Date */}
        <div>
          <label htmlFor="calculation_date" className="block text-sm font-medium text-gray-700 mb-2">
            <FiCalendar className="inline mr-2" />
            Calculation Date
          </label>
          <Controller
            name="calculation_date"
            control={control}
            rules={{ required: 'Calculation date is required' }}
            render={({ field }) => (
              <input
                {...field}
                type="date"
                id="calculation_date"
                max={format(new Date(), 'yyyy-MM-dd')}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.calculation_date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
            )}
          />
          {errors.calculation_date && (
            <p className="mt-1 text-sm text-red-600">{errors.calculation_date.message}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Tariff rates are applied based on this date
          </p>
        </div>

        {/* Summary Card */}
        {watchedHsCode && watchedCountry && watchedValue && (
          <div className="bg-gray-50 rounded-lg p-4 border">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Calculation Summary</h3>
            <div className="space-y-1 text-sm text-gray-600">
              <div>HS Code: <span className="font-mono">{watchedHsCode}</span></div>
              <div>
                Origin: {MAJOR_TRADING_PARTNERS.find(c => c.code === watchedCountry)?.name || watchedCountry}
              </div>
              <div>Value: ${formatCurrency(watchedValue)} AUD</div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className={`px-8 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Calculating...
              </div>
            ) : (
              'Calculate Duties'
            )}
          </button>
        </div>
      </form>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
        <h4 className="text-sm font-medium text-yellow-800 mb-2">Need Help?</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• HS Codes can be found using the Australian Border Force Tariff Classification tool</li>
          <li>• Customs value should include the cost of goods, insurance, and freight (CIF)</li>
          <li>• Country of origin determines applicable trade agreement rates</li>
          <li>• Results are estimates only - consult a licensed customs broker for official calculations</li>
        </ul>
      </div>
    </div>
  );
};

export default DutyCalculatorForm;