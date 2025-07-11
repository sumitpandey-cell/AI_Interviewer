import { useState } from 'react';
import { Play, Building, Clock, User, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useNavigate } from 'react-router-dom';
import { InterviewsAPI } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

const StartInterviewCard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    title: 'frontend dev',
    description: 'nothing',
    position: 'HR',
    company: 'TCS',
    interview_type: 'technical',
    duration_minutes: 60
  });

  const positions = [
    'Frontend Developer',
    'Backend Developer', 
    'Full Stack Developer',
    'HR',
    'Data Scientist',
    'Product Manager',
    'DevOps Engineer',
    'Mobile Developer'
  ];
  console.log('Positions:', positions);

  const interviewTypes = [
    { value: 'technical', label: 'Technical', color: 'bg-blue-500' },
    { value: 'behavioral', label: 'Behavioral', color: 'bg-green-500' },
    { value: 'system_design', label: 'System Design', color: 'bg-purple-500' },
    { value: 'coding', label: 'Coding', color: 'bg-orange-500' },
    { value: 'hr', label: 'HR', color: 'bg-pink-500' }
  ];

  const durations = [30, 45, 60, 90, 120];

  const handleInputChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true);
      console.log('Creating interview with data:', formData);
      
      // Create new interview using the API
      const interview = await InterviewsAPI.createInterview({
        title: formData.title,
        description: formData.description,
        interview_type: formData.interview_type,
        position: formData.position,
        company_name: formData.company,
        // Add other fields as needed by your backend
      });
      
      console.log('Interview created:', interview);
      
      toast({
        title: "Interview created",
        description: "Starting your interview session now...",
        duration: 3000,
      });
      
      // Navigate to live interview page with the interview ID
      navigate(`/interview?id=${interview.id}`);
    } catch (error) {
      console.error('Failed to create interview:', error);
      
      toast({
        variant: "destructive",
        title: "Failed to create interview",
        description: error instanceof Error ? error.message : "Please try again later.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl font-lovable text-white flex items-center space-x-2">
          <Play className="h-6 w-6 text-primary" />
          <span>Start New Interview</span>
        </CardTitle>
        <CardDescription className="text-muted">
          Configure your interview details and begin your preparation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Title */}
        <div className="space-y-2">
          <Label htmlFor="title" className="text-sm font-medium text-white flex items-center space-x-2">
            <FileText className="h-4 w-4" />
            <span>Interview Title</span>
          </Label>
          <Input
            id="title"
            placeholder="e.g., Frontend Developer Interview"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            className="bg-primary/10 border-primary/20 focus:border-primary text-white placeholder:text-muted"
          />
        </div>

        {/* Two column layout for Position and Company */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="position" className="text-sm font-medium text-white flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>Position</span>
            </Label>
            <Select value={formData.position} onValueChange={(value) => handleInputChange('position', value)}>
              <SelectTrigger className="bg-primary/10 border-primary/20 focus:border-primary text-white">
                <SelectValue placeholder="Select position" />
              </SelectTrigger>
              <SelectContent className="bg-card-bg border-primary/20">
                {positions.map((position) => (
                  <SelectItem key={position} value={position} className="text-white hover:bg-primary/20">
                    {position}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="company" className="text-sm font-medium text-white flex items-center space-x-2">
              <Building className="h-4 w-4" />
              <span>Company</span>
            </Label>
            <Input
              id="company"
              placeholder="e.g., TCS, Google, Microsoft"
              value={formData.company}
              onChange={(e) => handleInputChange('company', e.target.value)}
              className="bg-primary/10 border-primary/20 focus:border-primary text-white placeholder:text-muted"
            />
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description" className="text-sm font-medium text-white">
            Description (Optional)
          </Label>
          <Textarea
            id="description"
            placeholder="Add any specific notes or requirements for this interview..."
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="bg-primary/10 border-primary/20 focus:border-primary text-white placeholder:text-muted min-h-[80px]"
          />
        </div>

        {/* Interview Type and Duration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-sm font-medium text-white">Interview Type</Label>
            <div className="flex flex-wrap gap-2">
              {interviewTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleInputChange('interview_type', type.value)}
                  className={`px-3 py-2 rounded-lg border transition-all duration-200 flex items-center space-x-2 ${
                    formData.interview_type === type.value
                      ? 'border-primary bg-primary/20 text-primary'
                      : 'border-primary/20 text-muted hover:border-primary/40 hover:text-white'
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full ${type.color}`}></div>
                  <span className="text-sm">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-white flex items-center space-x-2">
              <Clock className="h-4 w-4" />
              <span>Duration (minutes)</span>
            </Label>
            <Select 
              value={formData.duration_minutes.toString()} 
              onValueChange={(value) => handleInputChange('duration_minutes', parseInt(value))}
            >
              <SelectTrigger className="bg-primary/10 border-primary/20 focus:border-primary text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-card-bg border-primary/20">
                {durations.map((duration) => (
                  <SelectItem key={duration} value={duration.toString()} className="text-white hover:bg-primary/20">
                    {duration} minutes
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Start Button */}
        <Button 
          onClick={handleSubmit}
          disabled={!formData.title || !formData.position || !formData.company || isSubmitting}
          className="w-full bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-white font-semibold py-3 transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          size="lg"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Preparing Interview...
            </>
          ) : (
            <>
              <Play className="h-5 w-5 mr-2" />
              Start {formData.interview_type.charAt(0).toUpperCase() + formData.interview_type.slice(1)} Interview
            </>
          )}
        </Button>

        {/* Preview Data */}
        {formData.title && (
          <div className="mt-4 p-4 bg-primary/5 rounded-lg border border-primary/10">
            <p className="text-xs text-muted mb-2">Interview Preview:</p>
            <div className="text-sm text-white space-y-1">
              <p><span className="text-muted">Title:</span> {formData.title}</p>
              <p><span className="text-muted">Position:</span> {formData.position}</p>
              <p><span className="text-muted">Company:</span> {formData.company}</p>
              <p><span className="text-muted">Type:</span> {formData.interview_type}</p>
              <p><span className="text-muted">Duration:</span> {formData.duration_minutes} minutes</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StartInterviewCard;
