<template>
  <ac-bound-field :field="form.fields.name"></ac-bound-field>
</template>

<script setup lang="ts">
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useForm} from '@/store/forms/hooks.ts'

const form = useForm('boundFields', {
  endpoint: '/',
  fields: {
    name: {value: 'Wat'},
    age: {value: 20},
  },
})
</script>
