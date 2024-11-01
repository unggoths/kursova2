from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class District(Base):
    __tablename__ = 'districts'
    district_id = Column(Integer, primary_key=True)
    district_name = Column(String, unique=True, nullable=False)
    properties = relationship("Property", back_populates="district")


class Property(Base):
    __tablename__ = 'properties'
    property_id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey('districts.district_id'))
    rooms = Column(Integer)
    area = Column(Float)
    budget = Column(Float)
    description = Column(Text)
    district = relationship("District", back_populates="properties")
    photos = relationship("Photo", back_populates="property")
    contacts = relationship("PropertyContact", back_populates="property")


class Contact(Base):
    __tablename__ = 'contacts'
    contact_id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    properties = relationship("PropertyContact", back_populates="contact")


class PropertyContact(Base):
    __tablename__ = 'property_contacts'
    property_id = Column(Integer, ForeignKey('properties.property_id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.contact_id'), primary_key=True)
    property = relationship("Property", back_populates="contacts")
    contact = relationship("Contact", back_populates="properties")


class Photo(Base):
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.property_id'))
    photo_path = Column(Text)
    property = relationship("Property", back_populates="photos")
