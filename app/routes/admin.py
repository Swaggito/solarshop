from flask import render_template, flash, redirect, url_for, request
from app import db
from app.models import Settings
from app.forms import (GeneralSettingsForm, ContactSettingsForm, 
                      SMTPSettingsForm, AddressSettingsForm)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    # Initialize each form instance
    general_form = GeneralSettingsForm()
    contact_form = ContactSettingsForm()
    smtp_form = SMTPSettingsForm()
    address_form = AddressSettingsForm()
    
    # Get or create settings
    settings_obj = Settings.query.first()
    if not settings_obj:
        settings_obj = Settings()
        db.session.add(settings_obj)
        db.session.commit()
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'general_settings' and general_form.validate_on_submit():
            settings_obj.site_name = general_form.site_name.data
            settings_obj.description = general_form.description.data
            settings_obj.site_url = general_form.site_url.data
        elif form_type == 'contact_settings' and contact_form.validate_on_submit():
            settings_obj.contact_email = contact_form.contact_email.data
            settings_obj.sales_email = contact_form.sales_email.data
            settings_obj.support_email = contact_form.support_email.data
            settings_obj.phone_number = contact_form.phone_number.data
        elif form_type == 'smtp_settings' and smtp_form.validate_on_submit():
            settings_obj.smtp_server = smtp_form.smtp_server.data
            settings_obj.smtp_port = smtp_form.smtp_port.data
            settings_obj.smtp_username = smtp_form.smtp_username.data
            settings_obj.smtp_password = smtp_form.smtp_password.data
            settings_obj.smtp_use_tls = smtp_form.smtp_use_tls.data
        elif form_type == 'address_settings' and address_form.validate_on_submit():
            settings_obj.address_line1 = address_form.address_line1.data
            settings_obj.address_line2 = address_form.address_line2.data
            settings_obj.city = address_form.city.data
            settings_obj.state = address_form.state.data
            settings_obj.postal_code = address_form.postal_code.data
            settings_obj.country = address_form.country.data
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    
    # Pre-populate forms with existing settings data
    if settings_obj:
        general_form.site_name.data = settings_obj.site_name
        general_form.description.data = settings_obj.description
        general_form.site_url.data = settings_obj.site_url
        
        contact_form.contact_email.data = settings_obj.contact_email
        contact_form.sales_email.data = settings_obj.sales_email
        contact_form.support_email.data = settings_obj.support_email
        contact_form.phone_number.data = settings_obj.phone_number
        
        smtp_form.smtp_server.data = settings_obj.smtp_server
        smtp_form.smtp_port.data = settings_obj.smtp_port
        smtp_form.smtp_username.data = settings_obj.smtp_username
        smtp_form.smtp_use_tls.data = settings_obj.smtp_use_tls
        
        address_form.address_line1.data = settings_obj.address_line1
        address_form.address_line2.data = settings_obj.address_line2
        address_form.city.data = settings_obj.city
        address_form.state.data = settings_obj.state
        address_form.postal_code.data = settings_obj.postal_code
        address_form.country.data = settings_obj.country
    
    return render_template('admin/settings.html', settings=settings_obj,
                           general_form=general_form,
                           contact_form=contact_form,
                           smtp_form=smtp_form,
                           address_form=address_form)
        forms['address_form'].address_line2.data = settings.address_line2
        forms['address_form'].city.data = settings.city
        forms['address_form'].state.data = settings.state
        forms['address_form'].postal_code.data = settings.postal_code
        forms['address_form'].country.data = settings.country

    return render_template('admin/settings.html', settings=settings, **forms)
                         contact_form=contact_form,
                         smtp_form=smtp_form,
                         address_form=address_form)
