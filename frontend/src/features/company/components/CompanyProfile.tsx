import { useParams } from 'react-router';
import { useGetCompanyByIdQuery } from '../api';
import { CompanyDetails } from './CompanyDetails';

export const CompanyProfile = () => {
  const { id, ticker } = useParams<{ id: string; ticker: string }>();
  const {
    data: company,
    isLoading,
    isError,
  } = useGetCompanyByIdQuery(
    {
      id: id || '',
      ticker: ticker || '',
    },
    { skip: !ticker },
  );

  if (isLoading) return <div className="p-4">Loading...</div>;
  if (!id || isError || !company) return <div className="p-4 text-red-500">Company not found.</div>;

  return <CompanyDetails company_id={id} company={company} />;
};
