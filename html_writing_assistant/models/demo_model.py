from odoo import models, fields, api


class WritingAssistantDemo(models.Model):
    _name = 'writing.assistant.demo'
    _description = 'Writing Assistant Demo'
    _order = 'name'

    name = fields.Char('Document Name', required=True)
    content = fields.Html('Content', help='HTML content with writing assistant')
    description = fields.Text('Description')
    user_id = fields.Many2one('res.users', 'Author', default=lambda self: self.env.user)
    date_created = fields.Datetime('Created', default=fields.Datetime.now)
    
    @api.model
    def create_sample_data(self):
        """Create sample data for testing"""
        sample_content = """
        <p>This is a sample document to demonstrate the writing assistant capabilities.</p>
        <p>The writing assistant can help you improve your grammar, spelling, and overal style.</p>
        <p>It will analyize your text and provide suggestions for better clarity and readability.</p>
        <p>You can use this tool to enhance the quality of you writing significantly.</p>
        """
        
        self.create({
            'name': 'Sample Document',
            'content': sample_content,
            'description': 'A sample document with intentional errors for testing the writing assistant.'
        })
        
        return True
